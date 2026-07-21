# Formato: Container de Chunks EA (CTRL/SHOC/SHDR/SDAT/FILL)

> Classificação geral: ✅ **Confirmado** (estrutura de enquadramento) · 🟡/🔵 para semântica interna.
> Evidências: `scripts/chunk_explorer.py` sobre `GLBLDATA.PSX`, `CW/LOCJT/JT3.TRK`, `CW/FEND/FE.TRK`.
> Este é o formato mais importante do jogo — a "pedra de roseta". Usado em `GLBLDATA.PSX`,
> todas as pistas `.TRK` e, embutido, dentro de `FE.TRK`.

## 1. Enquadramento (framing) — ✅ Confirmado

O arquivo é uma sequência linear de chunks. Cada chunk:

```
offset  size  campo
  +0      4    FourCC, gravado INVERTIDO (little-endian de ASCII).
               Ex.: bytes "LRTC" no arquivo  => identificador lógico "CTRL".
  +4      4    u32 little-endian: tamanho TOTAL do chunk, INCLUINDO estes 8 bytes.
  +8   size-8  payload
```

O próximo chunk começa em `offset + size`. O parser percorre 835 KB de `JT3.TRK` e
12,8 MB de `GLBLDATA.PSX` inteiros sem dessincronizar — o enquadramento está correto.

### FourCCs observados

| No arquivo | Lógico | Papel (evidência) | Cl. |
|---|---|---|---|
| `LRTC` | **CTRL** | Chunk de controle/raiz. 1 por container (topo). | ✅ |
| `COHS` | **SHOC** | "Stream chunk": wrapper de enquadramento; carrega SHDR ou SDAT. | ✅ |
| `RDHS` | **SHDR** | Header de seção (precede blocos de SDAT). | ✅ |
| `TADS` | **SDAT** | Bloco de dados (o conteúdo real). | ✅ |
| `LLIF` | **FILL** | Padding de alinhamento. | ✅ |
| `RVWS` | **SWVR** | Sub-container de áudio/stream EA (mesmo dos `.AV`), embutido em `FE.TRK`. | ✅ |
| `MGAV` | **VAGM** | Áudio VAG (ADPCM PS1), dentro dos SWVR de `FE.TRK`. | 🟡 |

## 2. Alinhamento a setor de CD — ✅ Confirmado (achado forte)

**Todo chunk `FILL` termina exatamente num múltiplo de 2048 bytes** (verificado: `end % 2048 == 0`
em 100% dos FILL de `JT3.TRK`). 2048 = tamanho do setor Form1 do CD. Interpretação:

> O container foi projetado para ser lido/DMA em blocos de setor. O jogo provavelmente
> carrega o arquivo em pedaços de 2048 bytes e processa chunk a chunk em streaming,
> por isso o `FILL` "empurra" o próximo bloco de dados para o início de um novo setor.

Isso é decisivo para o futuro Patch Builder: ao reescrever um container, **os blocos de dados
precisam permanecer alinhados a 2048**, senão o loader de streaming quebra.

## 3. Frames SHOC — 🟡 Provável

- Os `SHOC` de dados têm tamanho máximo de **4096 bytes** (payload 4088). Dados grandes são
  fatiados em vários SHOC/SDAT consecutivos de ~4 KB.
- O payload de um SHOC começa com **8 bytes** (frequentemente zerados) seguidos do sub-chunk
  `SHDR`/`SDAT`. Esses 8 bytes ainda não têm semântica confirmada (contador de frame? offset?).
  → 🔵 Hipótese a validar com o parser do executável (Fase 4).
- O `CTRL` raiz de `JT3.TRK` tem payload de 16 bytes: `00 00 00 00 00 80 2e 00 00 00 6c 00 00 c0 0c 00`
  — provavelmente contagem de seções e/ou tamanho total descomprimido. ❓

## 4. `GLBLDATA.PSX` vs `.TRK` — ✅ mesmo container

- `GLBLDATA.PSX` (12,3 MB): `CTRL` ×1 + `SHOC` ×81 + `FILL` ×1. É um único container grande
  com 81 seções (candidatos: modelos de carros, HUD, fontes, tabelas de física/power-ups).
- `JT3.TRK`: `CTRL` ×1 + `SHOC` ×277 + `FILL` ×17 (fatiamento em ~4 KB).
- `FE.TRK` (frontend, 20 MB): `CTRL` ×172 + `SWVR` ×172 + `SHOC` ×4751 + `VAGM` ×140 + `FILL` ×680.
  → o frontend é uma **concatenação de 172 sub-recursos**, cada um com seu container e áudio.

## 5. Semântica confirmada pelo parser do jogo — ✅ (2026-07-21)

RE de `FUN_8002a85c` (parser de stream) + `FUN_8002a2bc` (SHDR) + `FUN_8002a290` (cópia):

- **SHOC** é o frame; o sub-tag fica em **+0x10** do chunk: `SHDR` ou `SDAT`.
- **SHDR** declara um recurso. O **tipo** do recurso é um 4CC em **+0x18** (ex.: `Cpag`, `Ctrk`,
  `Cobj`, `Cact`, `Cvkb`…). Tamanhos em +0x30/+0x34; descritor a partir de +0x38.
- **SDAT** entrega bytes: copia `[chunk+0x14 .. chunk+size)` e **anexa** ao buffer do recurso atual
  (via cópia por palavras — `FUN_8002a290` é um memcpy). Quando o acumulado atinge o tamanho
  declarado, o recurso é finalizado. → **SDAT é remontagem crua; não há descompressão no stream.**
- **CTRL** guarda contagem de blocos de `0x6000` e tamanho total do recurso.
- **VAGB/VAGM** = áudio (upload de VAG/ADPCM para a SPU via `FUN_80022e50`).
- Descritores de recurso passam por uma **máquina de tokens** (`FUN_80067890`) — avaliador de
  atributos da EA (não é LZ). Alguns tipos podem ser comprimidos por essa via (a investigar).

### Tipos de recurso observados num `.TRK` (`scripts/extract_resources.py` em JT3.TRK → 48 recursos)

| 4CC | Provável significado | Qtde/ex. |
|---|---|---|
| `Cpag` | **Página de textura** (VRAM) | 13× (~43 KB) |
| `Ctrk` | Geometria da **pista** | 1× (50 KB) |
| `Cobj` | Objetos/modelos | vários |
| `Cvkb`/`Cvkh` | Veículo (corpo/header?) | 107 KB / 632 B |
| `Cact` | Atores/entidades | muitos (pequenos) |
| `Cshd`/`Ctos`/`Cnet`/`Cdcs`/`RPNS` | shading / diversos | 1× cada |

> Extrator disponível: `python3 scripts/extract_resources.py <container> <outdir>`.

## 6. Próximos experimentos

1. **Fase 4 (Ghidra):** achar a função que lê `CTRL`/`SHOC`. Ela revela: os 8 bytes de prefixo
   do SHOC, o significado do payload do CTRL, e se há descompressão (RefPack/EA?) no SDAT.
2. Dumpar todos os SDAT concatenados de um `.TRK` e analisar o blob resultante (geometria da pista?).
3. Verificar se algum SDAT está comprimido (checar entropia / assinatura RefPack `10 FB`).

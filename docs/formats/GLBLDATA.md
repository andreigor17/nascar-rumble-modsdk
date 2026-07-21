# `GLBLDATA.PSX` — Dados globais (carros, fontes, objetos)

> ✅ Estrutura mapeada (2026-07-21). Extração: `scripts/extract_resources.py` (resiliente a
> múltiplos containers). Contém os recursos globais do jogo, incluindo os **carros**.

## Estrutura

`GLBLDATA.PSX` (12,3 MB) = **172 containers `CTRL` concatenados** (mesmo padrão do `FE.TRK`),
separados por `FILL`. Cada sub-container agrupa os recursos de uma entidade.

Varredura do arquivo inteiro (1390 recursos com dados):

| Tipo | Qtde | Total | Significado |
|---|---:|---:|---|
| `Cpag` | 171 | 7,7 MB | **Páginas de textura / pinturas dos carros** (liveries) |
| `Cobj` | 693 | 2,9 MB | Modelos/objetos (peças dos carros e cenário) |
| `Ceng` | 171 | 163 KB | **Modelo 3D do carro** (não é stats — ver abaixo) |
| `Cvkb`/`Cvkh` | 1/1 | 181 KB | Corpo/header de veículo (template compartilhado?) |
| `Cfnt` | 6 | 21 KB | **Fontes** do jogo |
| `Csfx`/`Ctos`/`Cshd`/`Cctr` | 1 cada | — | SFX, e diversos globais |
| `SWVR` | 171 | — | Áudio por container (motor de cada carro?) |

## Descobertas

- Os **171 containers "de carro"** têm cada um: 1 `Cpag` (pintura) + `Cobj` (modelo) + `Ceng`
  (stats) + `SWVR` (áudio). Correspondem à grade de carros/pilotos.
- Pinturas confirmadas visualmente: carros de stock car com número, patrocínios e esquemas de
  cor reais — ex.: o **#43 do Richard Petty** (patrocínio EXIDE), pilotos reais da NASCAR.
  (Nas strings do EXE também há `Rick Carelli`, `Golf Cart`, `Jet Car`, `EA Sports Car`.)

## `Ceng` = modelo do carro (não stats) — ✅ estrutura, 🟡 malha

Handler `FUN_80022908` revela que `Ceng` é um container do **modelo 3D do carro**, por nível de
detalhe (LOD = byte em +3, valores 1–4). Cabeçalho:

```
+0x00  s16  = 1 (magic)
+0x02  u8   = 1
+0x03  u8   = nº de LODs
+0x08  s32  = offset do 1º bloco (0x1c)
+0x0c  s32  = tamanho do Cvkh (0x48 = 72)
+0x10  s32  = tamanho do Cvkb (0x1e0 = 480)
```

Cada LOD = `Cvkh` (header do veículo, 72 B — contém contadores: ~24 vértices, ~48 polígonos) +
`Cvkb` (geometria do corpo, 480 B, dados int16/SVECTOR). Renderizado por
`FUN_80022880(..., 'Cvkh'/'Cvkb', ...)`.

> **As stats de jogabilidade (velocidade/aceleração/direção) NÃO estão no `Ceng`** — o cabeçalho
> `Cvkh` é praticamente constante entre carros; o que varia é a geometria. As stats devem estar
> numa tabela do executável ou em outro recurso (ex.: tela de seleção no `FE.TRK`). A investigar.

**Próximo:** decodificar `Cvkb` (vértices + polígonos) → **Model Viewer** (primeiro carro 3D em OBJ).

```bash
python3 scripts/extract_resources.py extracted/GLBLDATA.PSX extracted/glbl_res   # extrai tudo
python3 scripts/decode_cpag.py extracted/glbl_res/cNNN_XXXX_Cpag.bin extracted/glbl_tex  # pintura -> PNG
```

## A fazer

- Mapear qual container = qual carro/piloto (via `Ceng` ou ordem) → catálogo de carros.
- Decodificar `Ceng` (stats) e `Cobj` (malha 3D do carro) → Model Viewer + Car Editor.

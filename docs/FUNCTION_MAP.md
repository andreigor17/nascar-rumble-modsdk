# FUNCTION_MAP — SLUS_010.68

> Semente da Fase 4, gerada por análise estática do executável (`scripts/exe_strings.py`),
> ANTES do Ghidra. Cada entrada é uma âncora: a string está no endereço indicado; a função que
> a referencia é o alvo a nomear no Ghidra. Classificação: ✅ Confirmado · 🟡 Provável · 🔵 Hipótese.
>
> Executável: PS-X EXE · load `0x80010000` · entry `0x800A5440` · t_size `0x9F800` · **sem overlays**.

## Funções identificadas via decompilação headless — ✅ (2026-07-21)

Pipeline PyGhidra (`scripts/ghidra/export_analysis.py`) analisou o EXE e exportou **2008 funções**,
`strings_xref.csv` e `decomp_all.c` (todas decompiladas). Xrefs resolvem as âncoras:

| Endereço | Nome sugerido | Papel (evidência) |
|---|---|---|
| `0x8002baa8` | `resource_stream_init` | Carrega `GlblData.psx` / `*.trk`. Monta sistema de streaming de **4 slots** (buffers ~0x6000, slots de 0x1805 ints), abre o arquivo via `FUN_8001bf28`, e faz fallback p/ `"GlblData.psx"` se `DAT_800af6c8==0`. É o **loader central de recursos**. |
| `0x8001bf28` | `file_open` | Abre arquivo por nome (retorna handle/índice usado numa tabela de 4 descritores em `DAT_800afc10`). |
| `0x80043520` | `ai_car_update` | Referencia `"AI Car %d (power = %ld/%ld)"`. Alvo p/ IA + sistema de power. |
| `0x800921a0` | `lsc_path_build` | Monta o caminho do `.lsc` (tela de load) conforme estado do jogo. |
| `0x80029be4` | `run_screen` | "Level/screen runner": `main` chama com `"Fe.trk"` (frontend) e depois em loop. |
| `0x800991e4` | `play_media_fullscreen` | Exibe `Intro.wve`/`Ea_logo.fsv` em 320×240 (0x140×0xf0). |
| `0x80079814` | `track_setup?` | Referencia a tabela de nomes de pista (`GR1.trk`…). |

**Estrutura global de estado:** `DAT_800af744` é um ponteiro p/ struct de estado do jogo; campo
`+0x10` = modo/estado atual (`main` faz loop lendo esse campo; valores 0 e 3 disparam recarga).

> Tabela de nomes das 22 pistas: ponteiros em `0x800abdd8`–`0x800abe40` (índice → `"XX?.trk"`).

## Sistema de recursos (lookup por tipo+id) — ✅ (2026-07-22)

- `0x80018788` **`res_find(type, id)`** — percorre a lista encadeada `DAT_800af5b0` e retorna o
  recurso cujo `+0x18==type` e `+0x1c==id`. É assim que o jogo pega qualquer recurso carregado.
- `0x80022880` **`res_register(data, size, type, id, alloc)`** — cria o nó do recurso: `+0x18=type`,
  `+0x1c=id`, `+0x20=size`, e copia os dados. Registra no sistema acima.
- `0x8003d128` **`car_slot_alloc()`** — devolve um slot 0..7 (`DAT_800af83b`); cada carro numa
  corrida ocupa um slot. Cvkh/Cvkb do carro são registrados com `id = slot`, não o índice do modelo.
- Ids de `Cobj` (peças) derivam de `(carId-1000)*10 + 0x2711`.

> **Conclusão sobre roster→livery:** o mapeamento índice-do-modelo → container/livery não é uma
> constante estática simples — a livery é resolvida no carregamento do carro para um slot. O jeito
> limpo de obter o mapeamento 1:1 é **dinâmico** (no emulador: selecionar cada carro e ler qual
> recurso é carregado) — tarefa natural da Fase 5 (RAM Map / Memory Inspector).

## SDK e compilador — ✅ Confirmado

- **PsyQ (Sony/SN Systems)**: presença das strings de debug de `libgpu` (`ResetGraph`, `DrawSync`,
  `ClearOTag`, `DrawOTag`, `PutDrawEnv`, `LoadImage`, `GPU timeout:…`) e `libcd` (`CdInit`, `CdRead`).
  String `Sony Computer Entertainment` embutida. → decomp "matching" deve usar o **compilador PsyQ**.
- Build path do desenvolvedor: `C:\PSX\` (0x800af11c) e um módulo `Loader` (0x800af174).

## Bibliotecas / runtime (PsyQ) — âncoras 🟡

| Área | Strings-âncora (RAM) | Alvo no Ghidra |
|---|---|---|
| GPU (libgpu) | `ResetGraph` 0x80012788 · `DrawSync` 0x8001280c · `DrawOTag` 0x800128b0 · `LoadImage` 0x8001285c | nomear wrappers de GPU |
| CD (libcd + camada EA) | `CdInit` 0x800121c0 · `CD_newmedia` 0x8001226c · `CD_cachefile` 0x8001234c · `CdRead` 0x80012630 | filesystem/loader de CD |
| DMA/IRQ | `DMA bus error` 0x80012700 · `unexpected interrupt` 0x800126c4 · `VSync: timeout` 0x80012680 | baixo nível |

> `CD_newmedia`/`CD_cachefile` parecem uma **camada de filesystem da EA** sobre a libcd (parseiam
> PVD, cacheiam diretório: `%d dir entries found`, `%d files found`). Alvo importante: é quem lê a ISO.

## Carregamento de recursos — 🟡 (alvo prioritário)

| String (RAM) | Papel provável |
|---|---|
| `GlblData.psx` 0x80010df0 | ponteiro p/ o nome do container global → achar o **loader de recursos** |
| `%sLoc%s\` 0x80011f68 · `%s%s%ld%c.lsc` 0x80011f4c | montagem de caminhos das pistas/telas |
| tabela de nomes `Fe.trk`,`JT3.trk`…`GR1.trk` em 0x800af35c–0x800af45c | **array de nomes das 22 pistas** (índice→pista) |

> A função que referencia essa tabela de `.trk` (0x800af35c+) é o **seletor de pista**. A que
> referencia `GlblData.psx` é o **carregador de dados globais**. Ambas destravam a Fase 6 (formatos).

## Gameplay — 🔵 (alvos da Fase 8)

| String (RAM) | Pista sobre o sistema |
|---|---|
| `AI Car %d (power = %ld/%ld)` 0x80011284 | **IA + sistema de "power"** (rubber-band?) — struct do carro de IA |
| `Launch Power-Up` 0x80011e24 · `Power-Ups:` 0x80010c94 · `Reduce Speed` 0x80011204 | **sistema de power-ups** (tabela de efeitos) |
| `Golf Cart` 0x800105f4 · `EA Sports Car` 0x8001061c · `Jet Car` 0x800af164 | **nomes de carros** (tabela de veículos) |
| `Rick Carelli` 0x800106dc | nome de piloto (tabela de pilotos NASCAR) |
| `lap %ld/%ld` · `Best Lap` · `Race Results for %s` · `Team %ld` | HUD/lógica de corrida |
| `Engine Volume:` · `Hand Brake/Horn` · `Brake/Reverse` | áudio de motor / input |

## Grid de oponentes — ✅ CONFIRMADO (estático + dinâmico, sessão 010, 2026-07-22)

Alvo do mod "campeonato com qualquer carro" **localizado e provado ao vivo** (PCSX-Redux, corrida de
Championship real: Jeff Gordon #24 Rookie, copa Gold Rush).

| Endereço | Nome | Papel |
|---|---|---|
| `0x8008927c` | **`grid_build` (FUN_8008927c)** | **Montador do grid / setup de corrida.** `switch(DAT_800b7115)` (modo) → define a contagem `DAT_800b0e40`, embaralha posições e **seleciona os model IDs dos oponentes** do pool da classe via RNG. Chamado dos 4 modos (Single/Champ/Time/Showdown). É **o único que escreve** as entradas de identidade do grid. **Hook alvo do mod.** |
| `0x800181ac` | **`rng_next` (FUN_800181ac)** | **RNG customizado** (lagged-Fibonacci, NÃO o rand PsyQ). Estado: tabela de 20 u32 em `DAT_800afa40`, índice `DAT_800af5a0` (decrementa; `tbl[i] += tbl[i+2 wrap]`). Confirmado em uso (índice=5, tabela com estado vivo). |
| `0x8003132c` | **`grid_spawn` (FUN_8003132c)** | **Lê** a tabela do grid e **instancia** cada carro posicionado na largada (fixed-point). Consome `puVar9=&DAT_800b0e40` (stride 8). Chamado de 0x16402 (setup da corrida). |

### Tabela de descritores do grid — `0x800b0e40` (✅ layout medido ao vivo)

`DAT_800b0e40` (byte) = **nº de carros** (=6 nesta corrida). Seguem **N entradas de 8 bytes**
(o byte de contagem coincide com o +0 da entrada 0). Layout por entrada:

| Off | Campo | Evidência (6 carros, todos Rookie) |
|---|---|---|
| +0 | flag (00 oponente / 01 jogador) | jogador tinha 01 |
| +1 | tipo: `0xff`=IA · `0x00`=jogador | 5×0xff + 1×0x00 |
| **+2** | **MODEL ID** (0–55 Rookie / +56 Pro / +112 Elite) | 35,30,26,1,32,**14** |
| +4 | ordem de grid (posição) | 05,04,03,02,01,00 |
| +5 | flag (classe/variante?) | 00/01 |
| +6,+7 | índice/ordenação interna | +7 = 01..05,00 |

**Cruzamento (`cars_wiki.csv`) — todos resolvem p/ pilotos Rookie válidos, e o +2 do jogador = o carro escolhido:**
`14`=Jeff Gordon(jogador) · `35`=Ron Hornaday · `30`=Bill Elliott · `26`=Kenny Wallace · `1`=Rusty Wallace · `32`=Jeff Burton.

### Como injetar qualquer carro (mod)

Escrever o **byte +2** de cada entrada de oponente na tabela `0x800b0e40` (ou +112 para Elite etc.),
**depois** de `grid_build` rodar e **antes** de `grid_spawn` instanciar. Para patch de ISO/RecompOne:
hookar `grid_build` (0x8008927c) forçando os IDs desejados no lugar da seleção por RNG. Pool/estado
auxiliar: `0x800b7068` (stride 0x18, handles por slot) e `0x800b7080` (stride 6, flags "usado").
Config do campeonato em `0x800b7168+`; modo em `0x800b7115` (=0x02 no Championship).

> ⚠️ Breakpoints do PCSX-Redux **só disparam no interpretador** — com `isDynarec:true` não firam.
> A confirmação aqui foi por **leitura de RAM ao vivo** (independe do dynarec) + xref estático.

## Próximos passos (no Ghidra)

1. Importar `SLUS_010.68`, rodar auto-análise.
2. Para cada string-âncora: duplo-clique → *References* → renomear a função que a usa.
3. Prioridade 1: função que lê `GlblData.psx` (loader) e a tabela de `.trk` (seletor de pista).
4. Prioridade 2: struct do "AI Car" a partir de `AI Car %d (power=…)` — abre física/IA.
5. Exportar ELF + map de símbolos → alimenta a Trilha B (RecompOne).

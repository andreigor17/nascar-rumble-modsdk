# FUNCTION_MAP — SLUS_010.68

> Semente da Fase 4, gerada por análise estática do executável (`scripts/exe_strings.py`),
> ANTES do Ghidra. Cada entrada é uma âncora: a string está no endereço indicado; a função que
> a referencia é o alvo a nomear no Ghidra. Classificação: ✅ Confirmado · 🟡 Provável · 🔵 Hipótese.
>
> Executável: PS-X EXE · load `0x80010000` · entry `0x800A5440` · t_size `0x9F800` · **sem overlays**.

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

## Próximos passos (no Ghidra)

1. Importar `SLUS_010.68`, rodar auto-análise.
2. Para cada string-âncora: duplo-clique → *References* → renomear a função que a usa.
3. Prioridade 1: função que lê `GlblData.psx` (loader) e a tabela de `.trk` (seletor de pista).
4. Prioridade 2: struct do "AI Car" a partir de `AI Car %d (power=…)` — abre física/IA.
5. Exportar ELF + map de símbolos → alimenta a Trilha B (RecompOne).

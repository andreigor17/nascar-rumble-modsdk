# Plano de Execução — NASCAR Rumble Reverse Engineering & ModSDK

> Documento derivado do [PRD](PRD_NASCAR_RUMBLE_REVERSE_ENGINEERING.md).
> Data: 2026-07-19. Status das descobertas: ✅ Confirmado · 🟡 Provável · 🔵 Hipótese · ❓ Desconhecido

## 0. O que já sabemos (análise inicial da ISO — 2026-07-19)

Análise feita diretamente sobre o dump `NASCAR Rumble (USA).bin/.cue` (sem modificá-lo):

| Fato | Status |
|---|---|
| Disco MODE2/2352, volume "RUMBLE", 111.075 setores (~261 MB) | ✅ |
| Boot: `SLUS_010.68` (serial SLUS-01068), executável PS-X EXE | ✅ |
| PS-X EXE: load address `0x80010000`, entry point `0x800A5440`, ~638 KB de código/dados | ✅ |
| `GLBLDATA.PSX` (12,8 MB) e os `.TRK` usam o MESMO container: chunks com 4CC invertido — `LRTC`→`CTRL`, `COHS`→`SHOC`, `RDHS`→`SHDR` | ✅ |
| `.AV` = container EA **SWVR** (`RVWS`) com chunks `FILE` (`ELIF`) e nomes embutidos (ex.: `...ssive__2.stream`) — formato já documentado pela comunidade (MultimediaWiki, usado em Future Cop: LAPD) | ✅ |
| `.WVE` = vídeos EA (chunk `VLC0` — família TGV/WVE da EA) | 🟡 |
| `.LSC` = "Loading SCreen"; header começa com dois u32 próximos (provável tamanho comprimido/descomprimido) → imagem comprimida | 🔵 |
| `DUMMY.DAT` (27 MB) = padding para posicionamento de setores | 🟡 |
| 8 "locations" em `CW/`: FEND (frontend), BB, BL, GR, JT, MC, MG, SE — cada uma com `XX.AV` (áudio/stream), `XXn.TRK` (pista) e `XXnA/B/C.LSC` (3 telas de load por pista) | ✅ |

**Consequência importante:** por ser um jogo EA de 1999/2000, boa parte dos formatos (SWVR, WVE, áudio EA) já tem documentação/ferramentas da comunidade. Não vamos partir do zero.

### Árvore da ISO (resumo)

```
/SYSTEM.CNF          ← boot config
/SLUS_010.68         ← executável principal (PS-X EXE)
/GLBLDATA.PSX        ← 12,8 MB, container CTRL/SHOC (dados globais: carros? fontes? HUD?)
/DUMMY.DAT           ← 27 MB de padding
/CW/
  ABOUTEA/  *.WVE    ← vídeos (créditos, produtoras)
  OPENING/  INTRO.WVE, LEGAL.LSC
  FEND/     FE.TRK (21 MB! frontend), FELD.LSC
  HELPSCRN/ HELP*.LSC, TIPS*.LSC
  LOCBB|BL|GR|JT|MC|MG|SE/   ← 7 localidades × (1 .AV + 3 .TRK + 9 .LSC)
```

---

## Fase 1 — Preparação do ambiente (1ª sessão)

**Objetivo:** ambiente reproduzível de análise e emulação.

### Tutorial de setup (macOS)

1. **Git + estrutura do repositório**
   ```bash
   cd /opt/Projetos/rumble
   git init
   mkdir -p docs ghidra tools extracted scripts emulator experiments saves notes
   ```
   Adicionar `.gitignore` para `*.bin`, `extracted/`, savestates (nunca versionar a ISO).
2. **Emuladores**
   - **DuckStation** (`brew install --cask duckstation`) — jogar, savestates, debugger básico.
   - **PCSX-Redux** — melhor debugger da atualidade para PS1: breakpoints, memória, **scripting em Lua**, GPU logging. Essencial para a Frente A.
   - **no$psx** é Windows-only; no macOS, PCSX-Redux cobre o mesmo papel.
3. **Ghidra**
   - `brew install --cask ghidra` (requer JDK 17+).
   - Instalar a extensão **ghidra_psx_ldr** (lab313/ghidra_psx_ldr no GitHub): carrega PS-X EXE, aplica mapa de memória do PS1 e assinaturas das bibliotecas PsyQ (fundamental — o jogo foi compilado com o SDK PsyQ da Sony, e reconhecer as funções da libc/libgpu/libspu elimina 50% do trabalho).
4. **Python 3 + ferramentas de análise**
   - `pip install kaitaistruct` — especificação formal dos formatos.
   - **ImHex** (`brew install --cask imhex`) — hex editor gratuito com pattern language (alternativa moderna ao 010 Editor).
   - **jpsxdec** — extração de vídeo/áudio padrão PS1 (útil para comparação).
5. **Ferramentas de ISO**
   - **dumpsxiso / mkpsxiso** (Lameguy64) — extrair e **reconstruir** ISOs de PS1 preservando LBAs. É a base do futuro Patch Builder.

**Critério de conclusão:** jogo rodando no DuckStation e no PCSX-Redux a partir do `.cue`; Ghidra abre o `SLUS_010.68` com memória mapeada; repositório Git inicializado.

---

## Fase 2 — Pesquisa da ISO → `ISO_TREE.md`

**Objetivo:** documentar todos os arquivos com LBA, tamanho, hash e hipótese de função.

1. Formalizar o script de parsing ISO9660/Mode2 já prototipado em `scripts/iso_tree.py`.
2. Gerar `docs/ISO_TREE.md` com: caminho, LBA, tamanho, SHA-1, magic bytes, classificação (✅🟡🔵❓).
3. Extrair todos os arquivos para `extracted/` (via script próprio ou `dumpsxiso`).
4. Confirmar a hipótese do `DUMMY.DAT` e mapear se há dados fora do filesystem (setores órfãos — comum em jogos EA que leem por LBA direto).

**Experimento-chave:** rodar o jogo no PCSX-Redux com log de leituras de CD e correlacionar *quando* cada arquivo é lido (menu → FE.TRK; corrida → XXn.TRK + XX.AV).

---

## Fase 3 — ISO Explorer (primeira ferramenta do SDK)

**Objetivo:** ferramenta CLI Python `tools/iso_explorer/` que:
- lista a árvore (`list`), extrai arquivos (`extract`), mostra hexdump/magic (`info`);
- entende Mode2/2352 nativamente (sem converter a ISO);
- serve de fundação para os parsers de formato (plugins por extensão).

Testes automatizados com hashes conhecidos. A partir daqui, todo formato novo vira um plugin.

---

## Fase 4 — Análise do executável → `FUNCTION_MAP.md`

**Objetivo:** mapear as funções do `SLUS_010.68`.

1. Importar no Ghidra com ghidra_psx_ldr; aplicar assinaturas PsyQ (identificar versão do SDK pelas strings — provável PsyQ 4.x).
2. Procurar strings: nomes de arquivos (`.TRK`, `.LSC`), mensagens de debug, printf's — cada string referenciada revela uma função de alto nível.
3. Identificar: `main`, loop principal, loader de arquivos (quem lê `GLBLDATA.PSX`?), parser dos chunks `CTRL`/`SHOC`/`SHDR` (essa função é a pedra de roseta dos formatos!).
4. Exportar o projeto Ghidra versionável em `ghidra/` (formato GZF) + gerar `docs/FUNCTION_MAP.md`.

**Atalho estratégico:** achar no executável o código que parseia os chunks nos dá a especificação exata do container, sem adivinhação.

---

## Fase 5 — Mapeamento da RAM → `RAM_MAP.md`

**Objetivo:** localizar as estruturas vivas do jogo.

Técnica principal: **memory diffing** no PCSX-Redux/DuckStation (cheat search):
- posição/velocidade do carro (mudar de posição → diff);
- power-up atual, contador de voltas, timer, dinheiro/pontos;
- estrutura do carro do jogador → array de carros da IA (mesmo layout, offsets consecutivos).

Cada endereço confirmado entra em `docs/RAM_MAP.md` com evidência (savestate + experimento). Esses endereços viram a base do **Memory Inspector** e do futuro Save Editor.

---

## Fase 6 — Formatos de arquivo (Kaitai + docs)

Ordem de ataque (do mais fácil/documentado para o mais difícil):

1. **Container CTRL/SHOC/SHDR** (`GLBLDATA.PSX`, `.TRK`) — estrutura de chunks primeiro, conteúdo depois. É o formato mais importante do jogo.
2. **`.LSC`** — provável imagem comprimida; alvo pequeno e com feedback visual imediato (quando decodificar, a tela de load aparece). Ótimo primeiro parser completo.
3. **`.AV` (SWVR)** — partir da documentação existente do MultimediaWiki/ScummVM (Future Cop usa o mesmo container).
4. **`.WVE`** — vídeos; baixa prioridade (não afeta gameplay).
5. **Save de Memory Card** — formato .mcd do emulador facilita: fazer save, diff, mapear.

Cada formato ganha: spec Kaitai (`docs/formats/*.ksy`), doc Markdown e parser Python no SDK.

---

## Fase 7 — Visualizadores (SDK read-only)

- **Texture Viewer**: texturas PS1 são TIM-like (4/8bpp + CLUT) dentro dos chunks — visualizador que varre um arquivo e tenta interpretar janelas de bytes como imagem ("texture ripping" assistido).
- **Track Viewer**: plotar geometria dos `.TRK` (mesh 3D → export glTF/OBJ).
- **Model Viewer**: modelos dos carros (provavelmente em `GLBLDATA.PSX`).
- **Memory Inspector**: leitura de RAM do emulador ao vivo (PCSX-Redux Lua bridge ou leitura de processo).

## Fase 8 — Gameplay research

Com RAM_MAP + FUNCTION_MAP: física (aceleração, grip), IA (rubber-banding), power-ups (tabela de efeitos), HUD. Experimentos via cheats/patches de RAM no emulador, sempre documentados em `experiments/`.

## Fase 9 — SDK de escrita + Patch Builder

- Editores (texture/car/track/save) = visualizadores + serialização inversa.
- **Patch Builder**: `mkpsxiso` para reconstruir a ISO com arquivos modificados preservando LBAs; distribuir mods como xdelta/PPF (nunca a ISO).
- Validação: ISO reconstruída sem mods deve ser **byte-idêntica** à original (teste de ouro do pipeline).

## Fase 10 — Decomp matching / port

Só depois das fases 4–8 maduras. Referências: CTR-ModSDK (CTR-tools), decomp.me para matching de funções MIPS (compilador PsyQ), estrutura tipo "splat" para separar código/dados.

---

## Próximos passos imediatos (proposta para a próxima sessão)

1. `git init` + `.gitignore` + commit do PRD e deste plano.
2. Instalar DuckStation, PCSX-Redux, Ghidra + ghidra_psx_ldr.
3. Escrever `scripts/iso_tree.py` (formalizando o protótipo) e gerar `docs/ISO_TREE.md`.
4. Primeira sessão de Ghidra: importar `SLUS_010.68`, aplicar assinaturas, catalogar strings.

## Referências externas

- MultimediaWiki — Electronic Arts Formats: https://wiki.multimedia.cx/index.php/Electronic_Arts_Formats
- ghidra_psx_ldr: https://github.com/lab313ru/ghidra_psx_ldr
- PCSX-Redux: https://pcsx-redux.consoledev.net/
- mkpsxiso/dumpsxiso: https://github.com/Lameguy64/mkpsxiso
- CTR-ModSDK (projeto de referência): https://github.com/CTR-tools/CTR-ModSDK
- psx-spx (documentação de hardware PS1, por Martin Korth/nocash): https://psx-spx.consoledev.net/

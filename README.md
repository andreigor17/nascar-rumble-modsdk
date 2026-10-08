# NASCAR Rumble — ModSDK & Reverse Engineering

🌐 **Site / Devlog:** https://rumble.irontech.dev.br/

[![Code matched](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fandreigor17%2Fnascar-rumble-modsdk%2Fmain%2Fprogress.json&query=%24.code.percent&suffix=%25&label=code%20matched)](progress.json)
[![Functions matched](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fandreigor17%2Fnascar-rumble-modsdk%2Fmain%2Fprogress.json&query=%24.functions.matched&label=functions%20matched)](progress.json)

> **PT-BR** · Projeto de engenharia reversa do **NASCAR Rumble** (PlayStation 1, EA, 2000).
> Objetivo atual: tornar o jogo original jogável como aplicativo nativo; melhorias gráficas e mods
> virão depois, sobre uma base fiel e estável.
>
> **EN** · Reverse engineering of **NASCAR Rumble** (PlayStation 1, EA, 2000). The current goal is
> to make the original game playable as a native app; graphics enhancements and mods will follow
> on a faithful, stable foundation.

## Status (2026-10)

- ✅ ISO mapeada (`docs/ISO_TREE.md`) · 108 arquivos.
- ✅ Executável analisado no Ghidra (headless/PyGhidra) · **2008 funções** · SDK PsyQ 4.6, sem overlays.
- ✅ **4 formatos decodificados**: container `CTRL/SHOC`, telas `.LSC` (MDEC), texturas `Cpag`, pistas `Ctrk`.
- ✅ Ferramentas do SDK (Python): explorador de ISO, extrator de recursos, decoders de textura/tela/pista.
- ✅ Toolchain PsyQ identificada e validada por funções *matching*.
- ✅ Split Splat integral e build híbrido ASM/dados do `SLUS_010.68`, idêntico byte a byte.
- ✅ Loop por função com asm-differ, objdiff, contexto local, backlog e primeiro C matching.
- 🟡 Port nativo macOS reproduz a intro, permite pulá-la, chega ao menu e entra em corrida com os
  carros apoiados na pista (bug do comando OP da GTE corrigido) e a corrida no ritmo do tempo real.
  Falta validar IA, uma corrida completa, HUD, áudio e retorno ao frontend.
- 🔒 O host nativo não carrega mods por padrão: a prioridade é intro, menu e corrida original.

Veja o progresso detalhado em [`docs/`](docs/) e nas notas de sessão em [`notes/`](notes/).
O ponto exato para retomar a investigação nativa está em
[`notes/SESSION_011.md`](notes/SESSION_011.md).
As métricas de decompilação vêm exclusivamente de [`progress.json`](progress.json), gerado a partir
do backlog e dos objetos registrados por `make progress-write`.

## Estrutura / Layout

```
docs/        documentação (PRD, plano, formatos, function map)
scripts/     ferramentas do SDK (Python) + scripts de Ghidra (PyGhidra)
config/      hashes, toolchains fixadas, Splat e símbolos importados
asm/         saída local regenerável do Splat (git-ignored)
linker/      linker script reproduzível gerado pelo Splat
ghidra_out/  índices exportados do Ghidra (functions.csv, strings_xref.csv)
notes/       diário de bordo por sessão
extracted/   (git-ignored) recursos extraídos da ISO — regeneráveis
```

## Build matching do executável

Com uma cópia legal extraída em `extracted/SLUS_010.68`:

```sh
make setup
make extract
make build
make check
```

O gate exige SHA-256 `e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75`
para a referência e para o rebuild. Detalhes em [`docs/SPLIT_BUILD.md`](docs/SPLIT_BUILD.md).

Para trabalhar em uma função sem remontar contexto manualmente no Ghidra:

```sh
make context FUNC=FUN_80078c24
make diff FUNC=FUN_80078c24
make objdiff FUNC=FUN_80078c24
make progress
```

Veja [`docs/DECOMP_WORKFLOW.md`](docs/DECOMP_WORKFLOW.md).

Antes de enviar mudanças, rode `make ci-public`; alterações no split ou em C também exigem
`make ci-full` com a referência local. Convenções e a política non-matching estão em
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Aviso legal / Disclaimer

Este é um **projeto de fã**, sem afiliação, patrocínio ou endosso da Electronic Arts. **Nenhum
asset ou cópia do jogo é distribuído** neste repositório. Para usar as ferramentas você precisa
da sua própria cópia legal do jogo. Marcas e conteúdos pertencem aos respectivos donos.
Ver [`DISCLAIMER.md`](DISCLAIMER.md).

Parte do trabalho é assistido por IA (Claude Code) sob revisão humana. / Part of this work is
AI-assisted (Claude Code) under human review.

## Licença

Código sob licença **MIT** (ver [`LICENSE`](LICENSE)). Documentação/textos podem ser reutilizados
com atribuição.

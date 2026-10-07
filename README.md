# NASCAR Rumble — ModSDK & Reverse Engineering

🌐 **Site / Devlog:** https://andreigor17.github.io/nascar-rumble-modsdk/

[![Code matched](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fandreigor17%2Fnascar-rumble-modsdk%2Fmain%2Fprogress.json&query=%24.code.percent&suffix=%25&label=code%20matched)](progress.json)
[![Functions matched](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fandreigor17%2Fnascar-rumble-modsdk%2Fmain%2Fprogress.json&query=%24.functions.matched&label=functions%20matched)](progress.json)

> **PT-BR** · Projeto de engenharia reversa e SDK de modding open source do jogo **NASCAR Rumble**
> (PlayStation 1, EA, 2000). Objetivo: compreender profundamente o jogo, documentar seus formatos
> e construir ferramentas de extração/edição — nos moldes do CTR-ModSDK. Projeto de longo prazo.
>
> **EN** · Reverse-engineering and open-source modding SDK for **NASCAR Rumble** (PlayStation 1,
> EA, 2000). Goal: deeply understand the game, document its file formats, and build extraction/
> editing tools — in the spirit of CTR-ModSDK. A long-term project.

## Status (2026-10)

- ✅ ISO mapeada (`docs/ISO_TREE.md`) · 108 arquivos.
- ✅ Executável analisado no Ghidra (headless/PyGhidra) · **2008 funções** · SDK PsyQ 4.6, sem overlays.
- ✅ **4 formatos decodificados**: container `CTRL/SHOC`, telas `.LSC` (MDEC), texturas `Cpag`, pistas `Ctrk`.
- ✅ Ferramentas do SDK (Python): explorador de ISO, extrator de recursos, decoders de textura/tela/pista.
- ✅ Toolchain PsyQ identificada e validada por funções *matching*.
- ✅ Split Splat integral e build híbrido ASM/dados do `SLUS_010.68`, idêntico byte a byte.
- ✅ Loop por função com asm-differ, objdiff, contexto local, backlog e primeiro C matching.

Veja o progresso detalhado em [`docs/`](docs/) e nas notas de sessão em [`notes/`](notes/).
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

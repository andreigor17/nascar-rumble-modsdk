# NASCAR Rumble — ModSDK & Reverse Engineering

> **PT-BR** · Projeto de engenharia reversa e SDK de modding open source do jogo **NASCAR Rumble**
> (PlayStation 1, EA, 2000). Objetivo: compreender profundamente o jogo, documentar seus formatos
> e construir ferramentas de extração/edição — nos moldes do CTR-ModSDK. Projeto de longo prazo.
>
> **EN** · Reverse-engineering and open-source modding SDK for **NASCAR Rumble** (PlayStation 1,
> EA, 2000). Goal: deeply understand the game, document its file formats, and build extraction/
> editing tools — in the spirit of CTR-ModSDK. A long-term project.

## Status (2026-07)

- ✅ ISO mapeada (`docs/ISO_TREE.md`) · 108 arquivos.
- ✅ Executável analisado no Ghidra (headless/PyGhidra) · **2008 funções** · SDK PsyQ 4.6, sem overlays.
- ✅ **4 formatos decodificados**: container `CTRL/SHOC`, telas `.LSC` (MDEC), texturas `Cpag`, pistas `Ctrk`.
- ✅ Ferramentas do SDK (Python): explorador de ISO, extrator de recursos, decoders de textura/tela/pista.

Veja o progresso detalhado em [`docs/`](docs/) e nas notas de sessão em [`notes/`](notes/).

## Estrutura / Layout

```
docs/        documentação (PRD, plano, formatos, function map)
scripts/     ferramentas do SDK (Python) + scripts de Ghidra (PyGhidra)
ghidra_out/  índices exportados do Ghidra (functions.csv, strings_xref.csv)
notes/       diário de bordo por sessão
extracted/   (git-ignored) recursos extraídos da ISO — regeneráveis
```

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

# Sessão 001 — 2026-07-19

## Objetivo
Executar Fase 1 (estrutura do repo) e Fase 2 (ISO_TREE), e iniciar a Fase 6 (formatos)
pelo container mais importante.

## Feito
- ✅ Estrutura do repositório criada + `.gitignore` (ISO nunca versionada).
- ✅ `scripts/iso_tree.py` — parser ISO9660 para MODE2/2352 (somente leitura). Gera
  `docs/ISO_TREE.md` + `docs/iso_tree.json` com LBA, tamanho, SHA-1, magic e classificação.
- ✅ `docs/ISO_TREE.md` gerado: 108 arquivos, 12 diretórios, volume `RUMBLE`.
- ✅ `scripts/chunk_explorer.py` — explorador do container de chunks EA.
- ✅ `docs/formats/CONTAINER_EA_CHUNKS.md` — estrutura do container documentada com evidência.
- ✅ Extraídos p/ análise: GLBLDATA.PSX, SLUS_010.68, JT3.TRK, FE.TRK, 2×LSC, BB.AV.

## Descobertas
- ✅ Container de chunks EA: `[4CC invertido][u32 tamanho-total][payload]`. Tags: CTRL(raiz),
  SHOC(frame), SHDR(header), SDAT(dados), FILL(padding), SWVR(áudio), VAGM(VAG).
- ✅ **FILL sempre termina em múltiplo de 2048** → container desenhado para streaming alinhado
  a setor de CD. Crítico para o futuro Patch Builder.
- ✅ GLBLDATA.PSX = 1 CTRL + 81 SHOC (mesmo container das pistas).
- ✅ FE.TRK = 172 sub-recursos CTRL+SWVR+VAG → frontend é concatenação de recursos com áudio.
- 🟡 SHOC de dados limitado a 4096 bytes (fatiamento).
- 🟡 `.LSC` = arquivo de 2 seções: `sizeA + sizeB + 8 == filesize` (exato). Header em `a0 00 00 01 ...`.
- 🔵 8 bytes de prefixo no payload do SHOC: semântica desconhecida (validar no Ghidra).

## Próximo passo (Sessão 002)
1. Instalar toolchain (DuckStation, PCSX-Redux, Ghidra + ghidra_psx_ldr) — ver Fase 1 do plano.
2. Ghidra: importar `SLUS_010.68`, aplicar assinaturas PsyQ, catalogar strings e achar o
   parser de CTRL/SHOC (destrava a semântica dos 8 bytes e detecta descompressão).
3. Alternativa sem Ghidra: dumpar todos os SDAT de `JT3.TRK` e analisar o blob (geometria?).

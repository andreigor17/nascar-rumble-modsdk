# Formato: `.LSC` — Telas de Loading (MDEC/BS)

> ✅ **Confirmado e decodificado** (2026-07-21). Evidência: RE de `FUN_80024c58` (load+display)
> e `FUN_80095d70` (decoder), + decodificação bem-sucedida com jpsxdec.
> Ferramenta: `scripts/decode_lsc.py`.

## Descoberta

As telas `.LSC` são **imagens comprimidas em MDEC "BS" v2** — o mesmo codec DCT dos vídeos `.STR`
do PS1, decodificado pelo hardware MDEC via `DecDCTin`/`DecDCTout` (libpress/PsyQ). Foi por isso
que o Ghidra aplicou assinaturas de `LIBPRESS`/`DCT002`.

## Layout do arquivo

```
+0x00  u32  sizeA         # tamanho da seção A
+0x04  u32  sizeB         # tamanho da seção B   (sizeA + sizeB + 8 == filesize)
+0x08  ...  seção A       # metade ESQUERDA da imagem
       ...  seção B       # metade DIREITA da imagem
```

Cada **seção**:
```
+0x00  u16  width         # ex.: 0x00A0 = 160
+0x02  u16  height        # ex.: 0x0100 = 256
+0x04  ...  frame BS       # bitstream MDEC padrão; magic 0x3800 em +0x02 do frame,
                           #   quant em +0x04, versão (0x0002) em +0x06
```

Prefixo EA = os 4 bytes `[width][height]`. Removendo-os, o restante é um frame BS **padrão**
que qualquer decodificador MDEC (ex.: jpsxdec) consome.

## Como o jogo monta (RE)

`FUN_80024c58`: carrega o arquivo e chama `FUN_80095d70` duas vezes —
seção A em VRAM Y=0, seção B em Y=0x100. As duas metades (160×256 cada) formam a imagem completa
**320×256** exibida como tela de loading.

## Decodificação (reproduzível)

```bash
python3 scripts/decode_lsc.py extracted/CW/HELPSCRN/HELP1.LSC extracted/lsc/png
# -> HELP1_A.png (esquerda), HELP1_B.png (direita), HELP1_full.png (320×256 combinada)
```

Resultado do `HELP1.LSC`: a tela "LOADING" com o controle DualShock e os mapeamentos
(Cameras, Horn, Steering, Launch Power-Up, Accelerate, Brake/Reverse, Pause…).

## Notas

- Todos os `.LSC` (HELP*, TIPS*, FELD, BB1A…, os 9 por localidade) devem seguir o mesmo formato.
- Para um **editor** de telas (SDK), o caminho inverso é recodificar um PNG para BS v2 (o jpsxdec
  tem o codificador) e reescrever `[sizeA][sizeB]` + prefixos. Alvo da Fase 7/9.
- `.WVE` (vídeos) provavelmente usam o mesmo MDEC em sequência de frames — a validar.

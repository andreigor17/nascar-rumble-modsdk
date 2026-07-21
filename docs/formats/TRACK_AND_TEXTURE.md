# Formatos: Textura (`Cpag`) e Pista (`Ctrk`)

> 🟡/✅ Parcialmente decodificados (2026-07-21). Ambos são recursos DENTRO do container
> `CTRL/SHOC` (ver [CONTAINER_EA_CHUNKS.md](CONTAINER_EA_CHUNKS.md)), extraíveis com
> `scripts/extract_resources.py`. Sub-chunks internos: `[4CC invertido][u32 size][data]`.

## `Cpag` — Página de textura ✅ (pixels) / 🟡 (paleta)

Sub-chunks observados: `tReg` (região) + pares (`PIX4`, `CLUT`) em 4 níveis de **mipmap**:
256×256, 128×128, 64×64, 32×32.

- **PIX4** = pixels **4bpp indexados** (2 pixels/byte, nibble baixo primeiro). Payload de 0x8000
  bytes no nível 0 = 256×256.
- **CLUT** = paleta. Cor PS1 15-bit (u16 LE): `bit15=STP`, `R=bits0-4`, `G=5-9`, `B=10-14` (×8).
- Handler no jogo: `FUN_8006710c` (dispatch de `0x43706167`).

**Estado:** decodificação de pixels **confirmada** — atlas real extraído (logo EA, "LEGEND",
rodas, emblemas). ✅
**A refinar:** atlas grandes têm **múltiplas CLUTs de 16 cores** (ex.: 496 cores = 31 paletas),
uma por sub-região. Para cores corretas é preciso associar cada região à sua CLUT via `TTEX`.
Também há variantes **8bpp** (`PIX8`?) a tratar. 🟡

Ferramenta: `python3 scripts/decode_cpag.py <res_Cpag.bin> <outdir>` → PNG por mipmap.

## `Ctrk` — Pista ✅ (traçado) / 🟡 (malha 3D)

Parser confirmado: `FUN_80062680` → `FUN_80062088`. Sub-chunks (JT3 tem 23):

| 4CC | Papel | Detalhe |
|---|---|---|
| `TCRV` | **Linha central** | N pontos de 10 bytes (5×int16): `(x, y, z, idx, flag)`. N=(size−0xc)/10 (=114 em JT3). y≈constante (altura do asfalto). |
| `TCOL` | Colisão | entradas u32 (o parser faz byte-swap). |
| `TTEX` | Mapeamento de textura | liga faces a páginas `Cpag`. |
| `TSEG` ×n | **Segmentos da malha** | ~2.4 KB cada (17 em JT3). Geometria 3D da estrada por segmento. |
| `THOR` | Horizonte/skybox | |
| `TIGR` | (grid/largada?) | |
| `TSUN` | Sol/iluminação | short << 7 = direção. |

**Estado:** traçado (centerline) **extraído e plotado** — JT3 é um **oval de NASCAR** (circuito
fechado, 114 pontos). ✅
**A fazer:** parsear `TSEG` para a malha 3D completa (vértices/faces) → export OBJ/glTF (Track Viewer). 🟡

Ferramenta: `python3 scripts/plot_track.py <res_Ctrk.bin> <out.png>` → mapa do traçado.

## Próximos passos

1. Associar CLUTs por região (via `TTEX`) para texturas com cores corretas.
2. Parsear um `TSEG` (vértices + faces) → primeiro mesh 3D exportável.
3. Rodar o extrator no `GlblData.psx` (modelos de carro, HUD, fontes globais).

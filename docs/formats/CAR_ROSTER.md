# Roster de carros / stats (tabela no executável)

> ✅ Decodificado (2026-07-21). Ferramenta: `scripts/dump_cars.py` → `docs/cars.csv`.

As stats de carro **não estão no `Ceng`** (que é o modelo 3D). Elas ficam numa **tabela de structs
no executável** (`SLUS_010.68`, ~file offset `0x9AF00`), com **32 carros**.

## Struct (12 bytes por carro)

| Off | Tipo | Campo | Notas |
|---|---|---|---|
| +0x00 | u32 | ponteiro do nome | string na zona `0x800105E0..` |
| +0x04 | u16 | **número do carro** | ex.: 43 (Richard Petty), 88 (Dale Jarrett), 153 (EA Sports Car) |
| +0x06 | u8 | **índice do modelo** | liga o carro ao container/livery no `GlblData.psx` |
| +0x07 | u8 | **rating** | desempenho ~20..63 (maior = melhor). Richard Petty=63, Adam Petty=20 |
| +0x08 | u8 | **classe** | 10/20/30/40/45 — casa com `"Class: "` na tela de seleção |
| +0x09 | 3×u8 | padding | zero |

## Observações

- Ordem: pilotos modernos (rating menor, classe 10–20) → **lendas** (Cale Yarborough, David
  Pearson, Bobby/Davey Allison, Richard Petty, Benny Parsons; rating 58–63, classe 20–40) →
  **EA Sports Car** (classe 45, especial).
- O **índice do modelo (+0x06)** é a ponte roster → livery/modelo 3D extraídos do `GlblData`.
- Veículos bônus (Golf Cart, Chicken Truck, Tow Truck, Road Captain) têm nomes na mesma zona,
  mas fora deste array de 32 — provável tabela/lógica separada (a investigar).
- Só há **um rating** por carro (não barras separadas de speed/accel/handling); a tela de seleção
  provavelmente deriva as barras do rating + classe. Uma tabela mais detalhada, se existir, fica a achar.

## Uso

```bash
python3 scripts/dump_cars.py            # imprime o roster
python3 scripts/dump_cars.py docs/cars.csv   # grava CSV
```

Base para o **Car Editor** (Frente B) e para a pesquisa de física/gameplay (Fase 8).

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

## Mapeamento roster → livery (parcial)

O disco tem **171 liveries** (`Cpag` no `GlblData`) = todas as pinturas reais da NASCAR da época,
bem além dos 32 carros do roster. O campo **índice do modelo (+0x06)** NÃO é o número do container
(testado: container 15=#5 Kellogg's, 46=#24 DuPont, 110=#86, 141=#43 — mapeamento não-linear).

- ✅ Confirmado por número: **#43 = Richard Petty** (container 141) e **#86 = Stacy Compton** (110).
- 🔵 A tabela `índice do modelo → container/recurso` é indireta (o roster em RAM `0x800AA700` é
  acessado por ponteiro; não há referência absoluta no decomp). **Próximo passo:** achar a função
  que carrega a livery a partir do índice do modelo para completar o mapeamento 1:1.

Base para o **Car Editor** (Frente B) e para a pesquisa de física/gameplay (Fase 8).

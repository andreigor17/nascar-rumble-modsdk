# RAM_MAP — NASCAR Rumble (memória viva)

> Endereços confirmados por *memory diffing* ao vivo no PCSX-Redux (`scripts/memsearch.py`).
> RAM começa em `0x80000000`. Classificação: ✅ Confirmado · 🟡 Provável · 🔵 Hipótese.

## Corrida / carros

| Endereço | Tipo | Campo | Ev. | Notas |
|---|---|---|:--:|---|
| `0x801a2e00` | u8 | **Volta (jogador?)** | ✅ | Rastreado 1→2→3 (reset→0→1→2) em sincronia com o HUD. **0-indexado** (HUD "1/4" = valor 0). Endereço mais baixo → provável carro 0 = jogador. |
| `0x801a4204` | u8 | Volta (outro carro?) | 🟡 | Mesma progressão; `0x1404` acima do anterior. |

**Bloco de dados de carros ~`0x801a2e00`** 🔵 — os dois contadores de volta ficam nesse bloco.
Testando `stride 0x1404`: carro[0]=`0x801a2e00`, carro[1]=`0x801a4204` (ambos volta=2 na corrida),
carros seguintes zerados (poucos ativos?). Bytes logo após a volta diferem por carro (candidatos a
posição/progresso). A confirmar se é o array de carros e qual o layout da struct.

## Como foi achado (reprodutível)

Busca `u8`: `eq 1`(34k) → volta → `eq 2`(163) → não seguiu (contador é 0-indexado). Refeito:
`eq 2`(43k, HUD 3/4) → `eq 3`(42) → nova corrida `eq 0`(10) → `eq 1`(3) → `eq 2`(2). Restaram
`0x801a2e00` e `0x801a4204`.

## Próximos alvos

- **Velocidade** e **posição (X,Y,Z)** do carro do jogador → confirmam a base da struct do jogador
  e o offset do contador de volta dentro dela.
- A partir da struct, mapear o **array de carros da IA** (mesmo layout, offsets seguidos).
- Escrita na memória (via console Lua do PCSX-Redux) para (a) fixar qual é o jogador e (b) cheats.

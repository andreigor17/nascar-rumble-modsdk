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

| `0x801a2ee8` | 4×u32 | **Vetor de velocidade (Vx,Vy,Vz,?) do jogador?** | 🟡 | Achado por diffing u32 (0 parado → grande na máxima). 4 valores adjacentes com magnitudes distintas, logo após o contador de volta do jogador (`0x801a2e00 + 0xe8`). Forte candidato à velocidade/velocidade-vetorial do jogador. A confirmar por escrita (Lua). |

> **Velocidade (magnitude):** o diffing por direção (aumentou/diminuiu) pega dezenas de valores
> físicos que escalam com a velocidade — muitos carros compartilham `máx=6144=0x1800`. O vetor em
> `0x801a2ee8` é o candidato mais forte por ficar dentro da struct do jogador. Confirmação definitiva
> pede **escrita na memória** (console Lua do PCSX-Redux) — próximo passo.

## Velocidade

| Endereço | Tipo | Campo | Ev. | Notas |
|---|---|---|:--:|---|
| `0x800b2d64` | u16 | **Velocidade exibida (HUD)** | ✅ | Achado autonomamente (Claude dirigindo). Bateu com o velocímetro em 4 pontos: 105→40→113→14. |
| `0x800c0a28` | u16 | Velocidade (cópia/HUD) | ✅ | Idêntico ao anterior em todos os pontos (mirror do valor de velocidade). |

> Controles confirmados: **CROSS = acelerar**, **SQUARE = frear/ré**. A velocidade exibida é
> **inteiro em MPH**. Achado 100% autônomo: Claude navegou os menus, dirigiu, leu o HUD e correlacionou a RAM.
>
> ✅ **LEITOR DE VELOCIDADE ESTÁVEL (2026-07-22):** a velocidade fica **dentro da struct do carro**,
> que é realocada a cada corrida — então endereços FIXOS (`0x800c0a28`) ficam obsoletos. A leitura
> correta e **race-independente** é via o ponteiro:
>
> ```
> car_ptr = *(u32*)0x800b6188          # ponteiro do carro do jogador (tabela de carros humanos)
> speed   = *(u16*)(car_ptr + 0xCC)    # velocidade exibida (MPH), = HUD
> ```
>
> Confirmado: com o carro no topo mostrando 161 no HUD, `*(u16*)(car_ptr+0xcc) == 161`. O offset
> `+0xCC` é constante; só o `car_ptr` muda por corrida. (Antes eu lia o endereço fixo e via 0 quando
> o ponteiro tinha mudado — daí a confusão.)
>
> **Velocidade máxima:** **161** = teto da classe **Rookie** (Jeff Gordon, medido). Os 181 do
> Copper Canyon eram Rookie 161 **+20 de um power-up de velocidade** (não ladeira/vácuo). Classes:
> Rookie ~160, Pro ~170, Elite ~180 (ver `docs/GAMEPLAY.md`). Savestate `_TOPSTRAIGHT`.

## Struct dos carros (tabela de ponteiros) — ✅ (2026-07-22)

- **`0x800b6188`** = **tabela de ponteiros dos carros dos jogadores humanos** (stride 0x40; getter
  em `FUN_80045590`; `(&DAT_800b6188)[i*0x10]` = ponteiro do carro do jogador `i`). Em single-player
  só o índice 0 é válido (os carros da IA ficam em OUTRA estrutura, a localizar).
- **Struct-entidade do jogador** = ponteiro dinâmico da tabela (ex.: `0x800c095c`). A velocidade
  (`0x800c0a28`) fica em `struct+0xcc`.
- **`carro+0x22`** = byte de **tipo/controle** (0x01/0x11). `FUN_80043520` (update de carro; imprime
  "AI Car power") só processa carros com +0x22 ∈ {0x01,0x11}. `param_1==0` = jogador (hardcoded).

> **Foothold para "IA dirige o P1":** achar as structs dos carros da IA + o flag humano/CPU. Viável,
> mas investigação de código de várias etapas. Ponto de partida: tabela `0x800b6188` e byte `+0x22`.

## Como foi achado (reprodutível)

Busca `u8`: `eq 1`(34k) → volta → `eq 2`(163) → não seguiu (contador é 0-indexado). Refeito:
`eq 2`(43k, HUD 3/4) → `eq 3`(42) → nova corrida `eq 0`(10) → `eq 1`(3) → `eq 2`(2). Restaram
`0x801a2e00` e `0x801a4204`.

## Próximos alvos

- **Velocidade** e **posição (X,Y,Z)** do carro do jogador → confirmam a base da struct do jogador
  e o offset do contador de volta dentro dela.
- A partir da struct, mapear o **array de carros da IA** (mesmo layout, offsets seguidos).
- Escrita na memória (via console Lua do PCSX-Redux) para (a) fixar qual é o jogador e (b) cheats.

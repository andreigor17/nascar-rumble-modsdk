# Gameplay / mecânicas (pesquisa da Fase 8)

> Conhecimento de mecânica do jogo, confirmado por medição ao vivo (PCSX-Redux) e/ou informado
> por quem conhece o jogo. Classificação: ✅ Confirmado · 🟡 Provável · 🔵 Hipótese.

## Classes de velocidade (Rookie / Pro / Elite)

Na seleção de carro dá para escolher a **classe** do carro (`Rookie` / `Pro` / `Elite`,
"Change Class ↕"). A classe define a **velocidade máxima**:

| Classe | Velocidade máxima |
|---|---|
| **Rookie** | ~160 / 161 |
| **Pro** | ~170 / 171 |
| **Elite** | ~180 / 181 |

- ✅ **Confirmado por medição:** Jeff Gordon #24 em **Rookie** = **161** (leitor estável
  `*(u16*)(*(0x800b6188)+0xCC)`, batendo com o HUD).
- 🟡 Pro (170/171) e Elite (180/181) informados pelo usuário — a verificar com o mesmo leitor.

## Power-up de velocidade

- **+20** de velocidade ao pegar o power-up de velocidade (temporário).
- ✅ Explica a leitura de **181** no Copper Canyon: era Rookie (161) **+20 do power-up**
  (antes eu havia especulado "ladeira/vácuo" — estava errado).

## Catálogo completo: 168 carros = 56 pilotos × 3 classes — ✅

Confirmado por uma guia da comunidade (fandom `NASCAR_Rumble_Cars_Guide`, via API do MediaWiki) e
cruzado com o nosso roster do EXE:

- **168 carros** = **56 pilotos** repetidos em **3 classes**. O índice de modelo (byte/HEX ID)
  codifica **classe + piloto**:
  - `id 0–55`  = **Rookie** 1–56 (Steve Park … #707 Road Captain)
  - `id 56–111` = **Pro** 1–56 (mesmos pilotos)
  - `id 112–167` = **Elite** 1–56 (mesmos pilotos)
- ✅ **Bate com o nosso roster** (`docs/cars.csv`): o campo `model` = o byte/ID da wiki para os
  pilotos "regulares" (ex.: model 15 = Rookie 25 Wally Dallenbach; 16 = Johnny Benson; 18 = Mike
  Skinner; 30 = Bill Elliott; 32 = Jeff Burton — todos batem).
- Isso **fecha o mapeamento índice-do-modelo → piloto/classe → livery** (que antes eu tentara achar
  por memory diffing). Cada `Cpag` (livery, ~171 no `GlblData`) corresponde a um desses IDs.
- O 56º "piloto" de cada classe é o bônus **#707 Road Captain** (e há outros especiais tipo
  EA Sports Car, Golf Cart, Jet Car nas faixas de bônus).
- Catálogo salvo em `docs/cars_wiki.csv` (id → nome com classe).
- 🟡 Os "Legends" (Richard Petty, Cale Yarborough…) no nosso roster usam índices que não batem 1:1
  com a faixa Rookie da wiki — provável conjunto/indexação separada (a investigar).

## A verificar (com controle autônomo + leitor estável)

- Medir o teto de Pro e Elite (trocar a classe na seleção e medir).
- Medir a duração e o valor exato do power-up de velocidade.
- Relacionar a classe (Rookie/Pro/Elite) com o campo **`class`** do roster (`docs/formats/CAR_ROSTER.md`)
  e com o **`rating`** por carro (aceleração/handling dentro da classe?).
- Outros power-ups (ver strings do EXE: "Launch Power-Up", "Reduce Speed", etc.) → tabela de efeitos.

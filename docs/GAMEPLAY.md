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

## A verificar (com controle autônomo + leitor estável)

- Medir o teto de Pro e Elite (trocar a classe na seleção e medir).
- Medir a duração e o valor exato do power-up de velocidade.
- Relacionar a classe (Rookie/Pro/Elite) com o campo **`class`** do roster (`docs/formats/CAR_ROSTER.md`)
  e com o **`rating`** por carro (aceleração/handling dentro da classe?).
- Outros power-ups (ver strings do EXE: "Launch Power-Up", "Reduce Speed", etc.) → tabela de efeitos.

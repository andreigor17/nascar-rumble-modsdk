# Sessão 010 (2026-07-22) — Caça à função do grid de oponentes

Método: RE dinâmico (PCSX-Redux, leitura de RAM ao vivo) + Ghidra (xref estático). ✅ ALVO ACHADO.

## Cadeia estática (Ghidra, ghidra_out/decomp_all.c)
- `FUN_8008927c` (0x8008927c) = **grid_build** — único writer das entradas de identidade do grid.
  switch(DAT_800b7115=modo) → seta DAT_800b0e40 (contagem) → seleciona oponentes via RNG.
  Callers: 0x61781 (param 1), 0x64773, 0x66443, 0x71973 (os 4 modos de corrida).
- `FUN_800181ac` (0x800181ac) = **RNG customizado** (lagged-Fibonacci): estado tbl[20]@DAT_800afa40,
  idx@DAT_800af5a0; `idx--; tbl[idx] += tbl[idx+2 (wrap 0..0x13)]`. NÃO é o rand PsyQ (0x41c64e6d).
- `FUN_8003132c` (0x8003132c) = **grid_spawn** — lê `&DAT_800b0e40` (stride 8) e instancia carros na
  largada. Callado de 0x16402. Slot setter/getter = FUN_8005e7d8/FUN_8005e7f0 (tabela 0x800b6188 stride 0x40).

## Captura ao vivo (Championship: Jeff Gordon #24 Rookie, copa Gold Rush, na pista, lap 1/4, P6/6)
DAT_800b0e40 = 6 (carros). Tabela 0x800b0e40 (hex, 64B):
```
06 ff 23 00 05 00 66 01  | e0 +2=0x23=35 Ron Hornaday   pos5
00 ff 1e 00 04 01 5a 02  | e1 +2=0x1e=30 Bill Elliott    pos4
00 ff 1a 00 03 01 4e 03  | e2 +2=0x1a=26 Kenny Wallace   pos3
00 ff 01 00 02 00 03 04  | e3 +2=0x01=1  Rusty Wallace   pos2
00 ff 20 00 01 01 60 05  | e4 +2=0x20=32 Jeff Burton     pos1
01 00 0e 00 00 00 2a 00  | e5 +2=0x0e=14 Jeff Gordon <== JOGADOR (flag +0=01,+1=00) pos0
```
- +2 = MODEL ID (0-55 Rookie / +56 Pro / +112 Elite). Todos Rookie (classe escolhida). ✅
- +1 = 0xff IA / 0x00 jogador; +0 = 01 no jogador; +4 = ordem de largada (5..0).
- Cruzamento model→piloto via docs/cars_wiki.csv bateu 6/6, e o +2 do jogador (14) = carro escolhido.
- RNG vivo: idx=5; tbl@0x800afa40 com estado pseudo-aleatório. Modo 0x800b7115=0x02.
- Player car ptr = *(0x800b6188) = 0x800c0860 (struct 0x40+; +0x22=0x01).

## Notas de método
- PCSX estava em DYNAREC → breakpoints do Redux NÃO firam (só no interpretador). _GRIDHIT ficou 0
  mesmo entrando na corrida. Confirmação foi por leitura de RAM (independe de dynarec) + xref.
- Canal Lua (/api/v1/lua/x) exige relançar com `-dofile scripts/pcsx_bootstrap.lua` (esta sessão
  subiu sem ele; relancei). Teclado de nome do campeonato: navegar 1 tap/0.4s (taps rápidos perdem).

## Mod "campeonato com qualquer carro"
Sobrescrever o byte +2 de cada entrada de oponente em 0x800b0e40 (após grid_build, antes de
grid_spawn) — ou, p/ ISO/RecompOne, hookar grid_build (0x8008927c) forçando os IDs. Pool aux:
0x800b7068 (stride 0x18) e 0x800b7080 (stride 6, flag usado). Config champ em 0x800b7168+.

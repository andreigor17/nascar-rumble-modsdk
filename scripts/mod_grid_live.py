#!/usr/bin/env python3
"""
mod_grid_live.py — lê/edita AO VIVO o grid de oponentes do NASCAR Rumble (PCSX-Redux).

É o banco de provas do mod `mods/champ_any_car` ANTES de virar patch de ISO: valida o
layout da tabela e, principalmente, descobre em QUE JANELA a injeção ainda funciona
(se os recursos/liveries do carro injetado chegam a ser carregados).

Tabela do grid (docs/FUNCTION_MAP.md): 0x800b0e40
  [+0] nº de carros; depois N entradas de 8 bytes:
  +0 flag(01=jogador) +1 tipo(0xff=IA, 0x00=jogador) +2 MODEL ID  +4 ordem de largada

Uso:
  python3 scripts/mod_grid_live.py show                 # despeja o grid atual com nomes
  python3 scripts/mod_grid_live.py set <i> <model>      # troca o model ID da entrada i
  python3 scripts/mod_grid_live.py opponents <m1> <m2>… # reescreve todos os oponentes
  python3 scripts/mod_grid_live.py class rookie|pro|elite  # move os oponentes de classe

model ID = piloto(0..55) + 56*classe   (0=Rookie, 56=Pro, 112=Elite)
"""
import sys, csv, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcsx

GRID = 0x800B0E40
MAX_CARS = 8
CLASSES = {"rookie": 0, "pro": 56, "elite": 112}
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def names():
    """model ID -> nome do piloto (docs/cars_wiki.csv)."""
    out = {}
    path = os.path.join(_REPO, "docs", "cars_wiki.csv")
    try:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                out[int(row["id"])] = row["name"]
    except Exception:
        pass
    return out


def read_grid():
    raw = pcsx.rd(GRID, 8 * MAX_CARS)
    n = raw[0]
    if not 1 <= n <= MAX_CARS:
        raise SystemExit(f"contagem de carros implausível ({n}) — está numa corrida?")
    return n, raw


def show():
    n, raw = read_grid()
    nm = names()
    print(f"carros no grid: {n}\n")
    print(f"{'ent':>3} {'tipo':<8} {'model':>5}  {'pos':>3}  piloto")
    print("-" * 58)
    for i in range(n):
        e = raw[i * 8:i * 8 + 8]
        kind = "JOGADOR" if e[1] == 0x00 else "IA"
        print(f"{i:>3} {kind:<8} {e[2]:>5}  {e[4]:>3}  {nm.get(e[2], '?')}")


def set_model(i, model):
    n, _ = read_grid()
    if not 0 <= i < n:
        raise SystemExit(f"entrada {i} fora do grid (0..{n-1})")
    pcsx.wr(GRID + i * 8 + 2, bytes([model & 0xFF]))
    print(f"entrada {i}: model -> {model}")


def set_opponents(models):
    """Aplica a lista em ordem às entradas de IA (nunca toca no jogador)."""
    n, raw = read_grid()
    k = 0
    for i in range(n):
        if raw[i * 8 + 1] == 0x00:      # jogador
            continue
        if k >= len(models):
            break
        pcsx.wr(GRID + i * 8 + 2, bytes([models[k] & 0xFF]))
        k += 1
    print(f"{k} oponente(s) reescrito(s)")
    show()


def set_class(cls):
    """Mantém os pilotos sorteados, mas move todos os oponentes para outra classe."""
    base = CLASSES[cls]
    n, raw = read_grid()
    k = 0
    for i in range(n):
        if raw[i * 8 + 1] == 0x00:
            continue
        pcsx.wr(GRID + i * 8 + 2, bytes([(raw[i * 8 + 2] % 56 + base) & 0xFF]))
        k += 1
    print(f"{k} oponente(s) -> {cls}")
    show()


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit()
    cmd = a[0]
    if cmd == "show":
        show()
    elif cmd == "set":
        set_model(int(a[1], 0), int(a[2], 0))
    elif cmd == "opponents":
        set_opponents([int(x, 0) for x in a[1:]])
    elif cmd == "class":
        set_class(a[1].lower())
    else:
        print("cmd?", cmd)

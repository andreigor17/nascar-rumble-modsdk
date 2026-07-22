#!/usr/bin/env python3
"""
memsearch.py — Cheat-search sobre a RAM ao vivo do PCSX-Redux (Web Server).

Lê a RAM (2 MB) via http://localhost:8080/api/v1/cpu/ram/raw e vai estreitando um
conjunto de endereços candidatos por comparação entre snapshots — a técnica clássica
de "memory diffing" para achar variáveis (voltas, velocidade, posição...).

Fluxo típico:
  python memsearch.py new u16          # snapshot A; candidatos = todos os u16 alinhados
  python memsearch.py eq 1             # mantém onde valor == 1 (ex.: volta 1)
  ...jogador muda o valor no jogo...
  python memsearch.py snap             # snapshot B
  python memsearch.py changed          # mantém onde mudou   (ou: eq 2 / inc / dec)
  python memsearch.py list             # mostra endereços candidatos + valores

Estado em experiments/ram/: cur.bin, prev.bin, search.json (+cands).
RAM começa em 0x80000000 (endereço = 0x80000000 + offset).
"""
import json
import sys
import urllib.request
from pathlib import Path
import numpy as np

URL = "http://localhost:8080/api/v1/cpu/ram/raw"
DIR = Path("experiments/ram")
BASE = 0x80000000
DT = {"u8": np.uint8, "u16": np.uint16, "u32": np.uint32}
WIDTH = {"u8": 1, "u16": 2, "u32": 4}


def fetch():
    with urllib.request.urlopen(URL, timeout=20) as r:
        return r.read()


def vals(data, w):
    n = len(data) // WIDTH[w]
    return np.frombuffer(data[:n * WIDTH[w]], dtype=DT[w])


def load_state():
    return json.loads((DIR / "search.json").read_text())


def save_state(s):
    (DIR / "search.json").write_text(json.dumps(s))


def snap():
    DIR.mkdir(parents=True, exist_ok=True)
    cur = DIR / "cur.bin"
    if cur.exists():
        cur.replace(DIR / "prev.bin")
    data = fetch()
    cur.write_bytes(data)
    return data


def cmd_new(w):
    assert w in DT, "largura: u8|u16|u32"
    data = snap()
    n = len(data) // WIDTH[w]
    np.save(DIR / "cands.npy", np.arange(n, dtype=np.uint32))
    save_state({"w": w})
    print(f"nova busca ({w}): {n:,} candidatos. Aplique 'eq <v>' ou mude o valor e use 'snap' + 'changed'.")


def _cands():
    return np.load(DIR / "cands.npy")


def _apply(mask_fn, label):
    s = load_state(); w = s["w"]
    cur = vals((DIR / "cur.bin").read_bytes(), w)
    prev_p = DIR / "prev.bin"
    prev = vals(prev_p.read_bytes(), w) if prev_p.exists() else None
    c = _cands()
    keep = mask_fn(c, cur, prev)
    c = c[keep]
    np.save(DIR / "cands.npy", c)
    print(f"{label}: {len(c):,} candidatos restantes")
    if len(c) <= 20:
        cmd_list(20)


def cmd_eq(v):
    _apply(lambda c, cur, prev: cur[c] == v, f"eq {v}")


def cmd_changed():
    _apply(lambda c, cur, prev: cur[c] != prev[c], "changed")


def cmd_unchanged():
    _apply(lambda c, cur, prev: cur[c] == prev[c], "unchanged")


def cmd_inc():
    _apply(lambda c, cur, prev: cur[c].astype(np.int64) > prev[c].astype(np.int64), "increased")


def cmd_dec():
    _apply(lambda c, cur, prev: cur[c].astype(np.int64) < prev[c].astype(np.int64), "decreased")


def cmd_list(n=30):
    s = load_state(); w = s["w"]
    cur = vals((DIR / "cur.bin").read_bytes(), w)
    c = _cands()
    print(f"{len(c):,} candidatos ({w}):")
    for idx in c[:n]:
        addr = BASE + int(idx) * WIDTH[w]
        print(f"  0x{addr:08x} = {int(cur[idx])}")


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    cmd = a[0]
    if cmd == "new": cmd_new(a[1])
    elif cmd == "snap": snap(); print("snapshot ok")
    elif cmd == "eq": cmd_eq(int(a[1], 0))
    elif cmd == "changed": cmd_changed()
    elif cmd == "unchanged": cmd_unchanged()
    elif cmd == "inc": cmd_inc()
    elif cmd == "dec": cmd_dec()
    elif cmd == "list": cmd_list(int(a[1]) if len(a) > 1 else 30)
    else: print("comandos: new|snap|eq|changed|unchanged|inc|dec|list")


if __name__ == "__main__":
    main()

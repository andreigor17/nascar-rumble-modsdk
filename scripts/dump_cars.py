#!/usr/bin/env python3
"""
dump_cars.py — Extrai a tabela de carros/pilotos do executável do NASCAR Rumble.

Descoberta por RE: array de structs de 12 bytes no EXE (~file 0x9af00):
  +0x00  u32  ponteiro para o nome (string na zona 0x800105e0..)
  +0x04  u16  número do carro (ex.: 43 = Richard Petty)
  +0x06  u8   índice do modelo/livery (container no GlblData.psx)
  +0x07  u8   rating de desempenho (~20..63; maior = melhor)
  +0x08  u8   classe/tier (10,20,30,40,45 — casa com "Class:" na UI)
  +0x09  3×u8 zero/padding

Uso: python3 scripts/dump_cars.py            # imprime tabela
     python3 scripts/dump_cars.py cars.csv   # também grava CSV
"""
import struct
import sys

BASE = 0x80010000
HDR = 0x800
NAME_LO, NAME_HI = 0x800105E0, 0x80010800
EXE = "extracted/SLUS_010.68"


def load():
    return open(EXE, "rb").read()


def read_cstr(d, ram):
    o = ram - BASE + HDR
    return d[o:d.index(b"\0", o)].decode("latin-1")


def find_array(d):
    """Acha o offset e a contagem do array de carros (structs de 12B com ptr de nome)."""
    best = None
    for base in range(0x9A000, 0x9C000, 4):
        cnt, oo = 0, base
        while oo + 12 <= len(d):
            p = struct.unpack_from("<I", d, oo)[0]
            if NAME_LO <= p < NAME_HI:
                cnt += 1; oo += 12
            else:
                break
        if cnt >= 10 and (best is None or cnt > best[1]):
            best = (base, cnt)
    return best


def cars(d):
    base, n = find_array(d)
    out = []
    for i in range(n):
        o = base + i * 12
        ptr = struct.unpack_from("<I", d, o)[0]
        num = struct.unpack_from("<H", d, o + 4)[0]
        model, rating, klass = d[o + 6], d[o + 7], d[o + 8]
        out.append({
            "idx": i, "name": read_cstr(d, ptr), "number": num,
            "model": model, "rating": rating, "class": klass,
        })
    return out


def main():
    d = load()
    rows = cars(d)
    print(f"# {len(rows)} carros no roster (EXE {EXE})\n")
    print(f"{'#':>2} {'Piloto/Carro':16} {'nº':>4} {'modelo':>6} {'rating':>6} {'classe':>6}")
    for c in rows:
        print(f"{c['idx']:2} {c['name']:16} {c['number']:4} {c['model']:6} {c['rating']:6} {c['class']:6}")
    if len(sys.argv) > 1:
        import csv
        with open(sys.argv[1], "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["idx", "name", "number", "model", "rating", "class"])
            w.writeheader(); w.writerows(rows)
        print(f"\n-> {sys.argv[1]}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
extract_resources.py — Extrai recursos de um container CTRL/SHOC do NASCAR Rumble,
seguindo EXATAMENTE a lógica do parser do jogo (FUN_8002a85c, confirmada no Ghidra):

  - Cada chunk: [4CC invertido][u32 tamanho total][payload].
  - SHOC com sub-tag (offset +16) == SHDR  -> inicia um novo recurso.
      * tipo do recurso: 4CC em +0x18 (ex.: Cpag, Cpyr, Cact, casC)
  - SHOC com sub-tag == SDAT -> anexa bytes [chunk+0x14 .. chunk+size) ao recurso atual.
  - CTRL / FILL / VAGB / VAGM: ignorados aqui (controle/áudio).

Cada recurso remontado é gravado em <out>/res_<n>_<tipo>.bin.

Uso: python3 scripts/extract_resources.py extracted/CW/LOCJT/JT3.TRK extracted/JT3_res
"""
import sys
import struct
from pathlib import Path


def rev(b):
    return b[::-1].decode("latin-1")


def main(path, outdir):
    data = Path(path).read_bytes()
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    off = 0
    resources = []
    cur = None
    counts = {}
    while off + 8 <= len(data):
        size = struct.unpack("<I", data[off + 4:off + 8])[0]
        if size < 8 or off + size > len(data):
            break
        name = rev(data[off:off + 4])
        counts[name] = counts.get(name, 0) + 1
        if name == "SHOC":
            subtag = rev(data[off + 16:off + 20])
            if subtag == "SHDR":
                typ = rev(data[off + 24:off + 28])          # +0x18
                declared = struct.unpack("<I", data[off + 0x30:off + 0x34])[0]
                cur = {"type": typ, "declared": declared, "data": bytearray()}
                resources.append(cur)
            elif subtag == "SDAT" and cur is not None:
                cur["data"] += data[off + 0x14:off + size]
        off += size

    print(f"# {path}  ({len(data):,} bytes)")
    print(f"# chunks: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"# recursos remontados: {len(resources)}\n")
    print(f"{'#':>3}  {'tipo':<6} {'declarado':>10} {'remontado':>10}  arquivo")
    for i, r in enumerate(resources):
        blob = bytes(r["data"])
        fn = out / f"res_{i:03d}_{r['type']}.bin"
        fn.write_bytes(blob)
        print(f"{i:3}  {r['type']:<6} {r['declared']:>10} {len(blob):>10}  {fn.name}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("uso: extract_resources.py <container> <outdir>"); sys.exit(1)
    main(args[0], args[1])

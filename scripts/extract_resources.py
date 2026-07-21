#!/usr/bin/env python3
"""
extract_resources.py — Extrai recursos de containers CTRL/SHOC do NASCAR Rumble,
seguindo o parser do jogo (FUN_8002a85c). Suporta arquivos com VÁRIOS containers
CTRL concatenados (ex.: GlblData.psx = 172 sub-containers; FE.TRK idem).

Chunk: [4CC invertido][u32 tamanho total][payload].
  SHOC + sub-tag(+0x10)=SHDR -> novo recurso (tipo 4CC em +0x18).
  SHOC + sub-tag=SDAT        -> anexa [chunk+0x14 .. chunk+size) ao recurso atual.
  CTRL/FILL/VAGB/VAGM        -> controle/áudio (ignorados aqui).
Se um chunk for inválido (fronteira entre containers/padding), faz RESYNC procurando
o próximo 4CC conhecido.

Uso: python3 scripts/extract_resources.py <arquivo> <outdir>
"""
import sys
import struct
from pathlib import Path

KNOWN_STORED = {b"LRTC", b"COHS", b"LLIF", b"RVWS", b"MGAV", b"BGAV"}  # tags top-level (invertidas)


def rev(b):
    return b[::-1].decode("latin-1", "replace")


def resync(d, off):
    """Avança até o próximo 4CC conhecido; retorna índice ou len(d)."""
    i = off
    while i < len(d) - 4:
        if d[i:i + 4] in KNOWN_STORED:
            return i
        i += 1
    return len(d)


def main(path, outdir):
    d = Path(path).read_bytes()
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    off = 0
    resources = []
    cur = None
    counts = {}
    n_ctrl = 0
    while off + 8 <= len(d):
        stored = d[off:off + 4]
        size = struct.unpack("<I", d[off + 4:off + 8])[0]
        # chunk inválido -> resync para a próxima fronteira conhecida
        if stored not in KNOWN_STORED or size < 8 or off + size > len(d):
            nxt = resync(d, off + 4)
            if nxt >= len(d):
                break
            off = nxt
            continue
        name = rev(stored)
        counts[name] = counts.get(name, 0) + 1
        if name == "CTRL":
            n_ctrl += 1
            cur = None  # cada container reinicia o recurso corrente
        elif name == "SHOC":
            subtag = rev(d[off + 16:off + 20])
            if subtag == "SHDR":
                typ = rev(d[off + 24:off + 28])
                cur = {"type": typ, "data": bytearray(), "container": n_ctrl}
                resources.append(cur)
            elif subtag == "SDAT" and cur is not None:
                cur["data"] += d[off + 0x14:off + size]
        off += size

    # grava e resume
    by_type = {}
    for i, r in enumerate(resources):
        blob = bytes(r["data"])
        if not blob:
            continue
        by_type.setdefault(r["type"], []).append(len(blob))
        dst = out / f"c{r['container']:03d}_{i:04d}_{r['type']}.bin"
        dst.write_bytes(blob)

    print(f"# {path} ({len(d):,} bytes)  containers CTRL: {n_ctrl}")
    print(f"# chunks: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"# recursos com dados: {sum(len(v) for v in by_type.values())}")
    for t, sizes in sorted(by_type.items(), key=lambda kv: -sum(kv[1])):
        print(f"  {t:6} x{len(sizes):<4} total={sum(sizes):>9,}  (ex.: {max(sizes):,} bytes)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        print("uso: extract_resources.py <container> <outdir>"); sys.exit(1)
    main(a[0], a[1])

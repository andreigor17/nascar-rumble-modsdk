#!/usr/bin/env python3
"""
plot_track.py — Extrai e plota o traçado (linha central) de uma pista .TRK/Ctrk.

Formato Ctrk (confirmado por RE — FUN_80062088):
  Sub-chunks [4CC invertido][u32 size][data]:
    TCRV — curva central: N pontos de 10 bytes (5×int16): (x, y, z, idx, flag). N=(size-0xc)/10.
    TCOL — colisão · TTEX — texturas · TSEG×n — segmentos da malha · THOR — horizonte · TSUN — sol.
  y é ~constante (altura do asfalto); plotar (x, z) dá o traçado visto de cima.

Uso: python3 scripts/plot_track.py extracted/JT3_res/res_017_Ctrk.bin extracted/track/JT3.png
"""
import struct
import sys
from pathlib import Path


def find_tcrv(d):
    off = 0
    while off + 8 <= len(d):
        tag = d[off:off + 4][::-1]
        size = struct.unpack("<I", d[off + 4:off + 8])[0]
        if size < 8 or off + size > len(d):
            break
        if tag == b"TCRV":
            return d[off + 0xc:off + size]
        off += size
    return None


def centerline(ctrk_bytes):
    body = find_tcrv(ctrk_bytes)
    if body is None:
        raise ValueError("sub-chunk TCRV não encontrado — é um Ctrk?")
    pts = []
    for i in range(0, len(body) - 9, 10):
        x, y, z, idx, flag = struct.unpack("<5h", body[i:i + 10])
        pts.append((x, y, z))
    return pts


def plot(ctrk_path, out_png):
    from PIL import Image, ImageDraw
    pts = centerline(Path(ctrk_path).read_bytes())
    xs = [p[0] for p in pts]; zs = [p[2] for p in pts]
    minx, maxx, minz, maxz = min(xs), max(xs), min(zs), max(zs)
    W = H = 700; pad = 40
    sx = lambda x: pad + (x - minx) / (maxx - minx) * (W - 2 * pad)
    sy = lambda z: pad + (z - minz) / (maxz - minz) * (H - 2 * pad)
    img = Image.new("RGB", (W, H), (18, 20, 28))
    dr = ImageDraw.Draw(img)
    poly = [(sx(x), sy(z)) for x, _, z in pts]
    dr.line(poly + [poly[0]], fill=(80, 200, 255), width=3)
    for px, py in poly:
        dr.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 120, 60))
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    print(f"{len(pts)} pontos · X {minx}..{maxx} Z {minz}..{maxz} · altura y~{pts[0][1]}")
    print(f"-> {out_png}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print("uso: plot_track.py <Ctrk.bin> [out.png]"); sys.exit(1)
    plot(a[0], a[1] if len(a) > 1 else "extracted/track/track.png")

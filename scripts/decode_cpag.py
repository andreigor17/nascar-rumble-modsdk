#!/usr/bin/env python3
"""
decode_cpag.py — Decodifica um recurso Cpag (página de textura) do NASCAR Rumble em PNG.

Estrutura do Cpag (confirmada por RE — sub-chunks [4CC invertido][u32 size][data]):
  tReg            — cabeçalho de região de textura
  PIX4 + CLUT     — nível de mipmap: pixels 4bpp indexados + paleta de 16 cores (15-bit PS1)
  (repete p/ 256x256, 128x128, 64x64, 32x32)

Cores PS1 15-bit (u16 little-endian): bit15=STP, bits0-4=R, 5-9=G, 10-14=B (cada canal *8).

Uso: python3 scripts/decode_cpag.py extracted/JT3_res/res_004_Cpag.bin extracted/tex
"""
import struct
import sys
from pathlib import Path


def rev4(b):
    return b[::-1].decode("latin-1")


def parse_chunks(d):
    """Percorre sub-chunks [4CC invertido][u32 size total incl. 8][payload]."""
    off = 0
    out = []
    while off + 8 <= len(d):
        tag = rev4(d[off:off + 4])
        size = struct.unpack("<I", d[off + 4:off + 8])[0]
        if size < 8 or off + size > len(d):
            break
        out.append((tag, off, size, d[off + 8:off + size]))
        off += size
    return out


def clut_to_rgb(clut_bytes):
    pal = []
    for i in range(0, len(clut_bytes), 2):
        c = struct.unpack("<H", clut_bytes[i:i + 2])[0]
        r = (c & 0x1F) << 3
        g = ((c >> 5) & 0x1F) << 3
        b = ((c >> 10) & 0x1F) << 3
        pal.append((r, g, b))
    return pal


def decode(path, outdir):
    from PIL import Image
    d = Path(path).read_bytes()
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    chunks = parse_chunks(d)

    # emparelha cada PIX4 com o CLUT que o segue
    levels = []
    pending_pix = None
    for tag, off, size, payload in chunks:
        if tag == "PIX4":
            pending_pix = payload
        elif tag == "CLUT" and pending_pix is not None:
            levels.append((pending_pix, payload))
            pending_pix = None

    stem = Path(path).stem
    print(f"# {path}: {len(chunks)} sub-chunks, {len(levels)} níveis de mipmap")
    made = []
    for lvl, (pix, clut) in enumerate(levels):
        npix = len(pix) * 2                         # 4bpp -> 2 pixels/byte
        side = int(round(npix ** 0.5))              # texturas são quadradas (256,128,64,32)
        pal = clut_to_rgb(clut)
        img = Image.new("RGB", (side, side))
        px = img.load()
        for i in range(min(npix, side * side)):
            byte = pix[i >> 1]
            idx = (byte & 0x0F) if (i & 1) == 0 else (byte >> 4)
            x, y = i % side, i // side
            if idx < len(pal):
                px[x, y] = pal[idx]
        fn = out / f"{stem}_mip{lvl}_{side}x{side}.png"
        img.save(fn)
        made.append(fn)
        print(f"  mip{lvl}: {side}x{side}, paleta {len(pal)} cores -> {fn.name}")
    return made


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("uso: decode_cpag.py <res_XXX_Cpag.bin> [outdir]"); sys.exit(1)
    decode(args[0], args[1] if len(args) > 1 else "extracted/tex")

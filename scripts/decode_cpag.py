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


def parse_regions(treg_payload):
    """tReg: registros de 12 bytes [x0,y0,x1,y1 (u8)][palIdx u16][2×u16][u16]."""
    regs = []
    for i in range(0, len(treg_payload) - 11, 12):
        r = treg_payload[i:i + 12]
        x0, y0, x1, y1 = r[0], r[1], r[2], r[3]
        pal = struct.unpack("<H", r[4:6])[0]
        regs.append((x0, y0, x1, y1, pal))
    return regs


def pix4_nibble(pix, x, y, side):
    i = y * side + x
    byte = pix[i >> 1]
    return (byte & 0x0F) if (i & 1) == 0 else (byte >> 4)


def decode(path, outdir):
    from PIL import Image
    d = Path(path).read_bytes()
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    chunks = parse_chunks(d)

    treg = next((p for t, o, s, p in chunks if t == "tReg"), None)
    levels = []
    pending_pix = None
    for tag, off, size, payload in chunks:
        if tag == "PIX4":
            pending_pix = payload
        elif tag == "CLUT" and pending_pix is not None:
            levels.append((pending_pix, payload))
            pending_pix = None

    regions = parse_regions(treg) if treg else []
    stem = Path(path).stem
    print(f"# {path}: {len(chunks)} sub-chunks, {len(levels)} mipmaps, {len(regions)} regiões")
    made = []
    for lvl, (pix, clut) in enumerate(levels):
        npix = len(pix) * 2
        side = int(round(npix ** 0.5))
        pal_all = clut_to_rgb(clut)                 # todas as paletas concatenadas
        npal = max(1, len(pal_all) // 16)
        img = Image.new("RGB", (side, side))
        px = img.load()

        # escala das regiões (definidas na página 256) para o nível atual
        scale = side / 256.0
        if regions and npal > 1:
            # colore cada região com sua própria paleta de 16 cores
            for (x0, y0, x1, y1, palidx) in regions:
                base = (palidx % npal) * 16
                pal = pal_all[base:base + 16]
                sx0, sy0 = int(x0 * scale), int(y0 * scale)
                sx1, sy1 = int(round(x1 * scale)), int(round(y1 * scale))
                for y in range(max(0, sy0), min(side, sy1 + 1)):
                    for x in range(max(0, sx0), min(side, sx1 + 1)):
                        idx = pix4_nibble(pix, x, y, side)
                        if idx < len(pal):
                            px[x, y] = pal[idx]
        else:
            pal = pal_all[:16]
            for i in range(min(npix, side * side)):
                idx = (pix[i >> 1] & 0x0F) if (i & 1) == 0 else (pix[i >> 1] >> 4)
                if idx < len(pal):
                    px[i % side, i // side] = pal[idx]

        fn = out / f"{stem}_mip{lvl}_{side}x{side}.png"
        img.save(fn)
        made.append(fn)
        print(f"  mip{lvl}: {side}x{side}, {npal} paleta(s) -> {fn.name}")
    return made


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("uso: decode_cpag.py <res_XXX_Cpag.bin> [outdir]"); sys.exit(1)
    decode(args[0], args[1] if len(args) > 1 else "extracted/tex")

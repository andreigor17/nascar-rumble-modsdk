#!/usr/bin/env python3
"""
decode_lsc.py — Decodifica uma tela de loading .LSC do NASCAR Rumble para PNG.

Formato .LSC (confirmado por RE — FUN_80024c58 / FUN_80095d70 no Ghidra):
  [u32 sizeA][u32 sizeB][seção A][seção B]     (sizeA + sizeB + 8 == tamanho do arquivo)
  Cada seção é uma metade (esquerda/direita) da imagem, comprimida em MDEC "BS" v2 do PS1.
  Layout da seção: [u16 width][u16 height][frame BS padrão começando com magic 0x3800].
  O jogo decodifica via libpress/MDEC (DecDCTin/DecDCTout) e monta na VRAM.

Este script separa as seções, remove o prefixo EA de 4 bytes e chama o jpsxdec
(decodificador MDEC padrão) para gerar um PNG por metade.

Requisitos: Java + jpsxdec.jar (ver tools/jpsxdec).
Uso: python3 scripts/decode_lsc.py extracted/CW/HELPSCRN/HELP1.LSC extracted/lsc/png
"""
import struct
import subprocess
import sys
from pathlib import Path

JAR = Path("tools/jpsxdec/jpsxdec_v2.1-beta/jpsxdec.jar")


def decode(lsc_path, outdir):
    lsc = Path(lsc_path)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    d = lsc.read_bytes()
    sizeA, sizeB = struct.unpack("<II", d[0:8])
    assert sizeA + sizeB + 8 == len(d), "tamanho inconsistente — não é um .LSC?"
    sections = {"A": d[8:8 + sizeA], "B": d[8 + sizeA:8 + sizeA + sizeB]}
    pngs = []
    for name, sec in sections.items():
        w, h = struct.unpack("<HH", sec[:4])          # prefixo EA: largura, altura
        bs = sec[4:]                                   # frame BS padrão (magic 0x3800 em +2)
        bs_file = out / f"{lsc.stem}_{name}.bs"
        bs_file.write_bytes(bs)
        subprocess.run(
            ["java", "-jar", str(JAR), "-f", str(bs_file),
             "-static", "bs", "-dim", f"{w}x{h}"],
            check=True, capture_output=True,
        )
        # jpsxdec grava <stem>.png no diretório atual — move para o outdir
        produced = Path.cwd() / f"{bs_file.stem}.png"
        png = out / f"{lsc.stem}_{name}.png"
        if produced.exists():
            produced.replace(png)
            pngs.append(png)
            print(f"  {name}: {w}x{h} -> {png.name}")
        bs_file.unlink(missing_ok=True)
    # tenta juntar as metades (esquerda|direita) se o Pillow estiver disponível
    try:
        from PIL import Image
        imgs = [Image.open(p) for p in sorted(pngs)]
        if len(imgs) == 2:
            full = Image.new("RGB", (imgs[0].width + imgs[1].width,
                                     max(i.height for i in imgs)))
            full.paste(imgs[0], (0, 0))
            full.paste(imgs[1], (imgs[0].width, 0))
            combined = out / f"{lsc.stem}_full.png"
            full.save(combined)
            print(f"  combinado -> {combined.name}")
    except ImportError:
        print("  (Pillow não instalado — metades geradas separadamente)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("uso: decode_lsc.py <arquivo.lsc> [outdir]"); sys.exit(1)
    decode(args[0], args[1] if len(args) > 1 else "extracted/lsc/png")

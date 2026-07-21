#!/usr/bin/env python3
"""
exe_strings.py — Extrai strings de um PS-X EXE já com o ENDEREÇO DE RAM calculado.

Num PS-X EXE, os dados começam no offset de arquivo 0x800 e são carregados em t_addr.
Logo, uma string no offset F (>=0x800) fica na RAM em: t_addr + (F - 0x800).

Saída: tabela ordenada por endereço, separando strings "interessantes" (format strings,
nomes de arquivo, mensagens de debug) que no Ghidra levam direto às funções que as usam.

Uso: python3 scripts/exe_strings.py extracted/SLUS_010.68
"""
import re
import struct
import sys

HEADER = 0x800  # tamanho do cabeçalho PS-X EXE


def main(path):
    d = open(path, "rb").read()
    assert d[:8] == b"PS-X EXE", "não é um PS-X EXE"
    pc0 = struct.unpack("<I", d[0x10:0x14])[0]
    t_addr = struct.unpack("<I", d[0x18:0x1c])[0]
    t_size = struct.unpack("<I", d[0x1c:0x20])[0]

    def ram(fileoff):
        return t_addr + (fileoff - HEADER)

    # acha strings ASCII imprimíveis de tamanho >= 4, com posição
    results = []
    for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
        off = m.start()
        if off < HEADER:
            continue
        s = m.group().decode()
        results.append((ram(off), off, s))

    def interesting(s):
        return ("%" in s) or s.lower().endswith(
            (".trk", ".lsc", ".av", ".wve", ".psx", ".cnf")
        ) or any(k in s.lower() for k in (
            "error", "found", "timeout", "fail", "load", "dir", "memory",
            "card", "save", "psyq", "sdk", "version", "\\"
        ))

    print(f"# {path}")
    print(f"# entry(pc0)=0x{pc0:08x}  load(t_addr)=0x{t_addr:08x}  t_size=0x{t_size:x}")
    print(f"# strings encontradas: {len(results)}\n")

    interesting_list = [r for r in results if interesting(r[2])]
    print(f"## Strings de interesse ({len(interesting_list)}) — âncoras p/ FUNCTION_MAP")
    print(f"{'RAM':<12} {'file':<8} texto")
    for ramaddr, off, s in interesting_list:
        print(f"0x{ramaddr:08x}  0x{off:06x}  {s!r}")

    # heurística de detecção de SDK/compilador
    print("\n## Pistas de SDK/compilador")
    blob = d.decode("latin-1")
    for kw in ("PsyQ", "Sony", "SN Systems", "GCC", "gcc", "SDEV", "libgs",
               "libgpu", "libspu", "libcd", "Metrowerks", "CodeWarrior"):
        if kw in blob:
            i = blob.find(kw)
            ctx = blob[max(0, i - 8):i + 24].replace("\n", " ")
            print(f"  encontrado {kw!r}: …{ctx!r}…")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "extracted/SLUS_010.68")

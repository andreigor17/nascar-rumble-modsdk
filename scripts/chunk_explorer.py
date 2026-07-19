#!/usr/bin/env python3
"""
chunk_explorer.py — Explorador do container de chunks da EA usado no NASCAR Rumble.

Formato observado (evidência): sequência de chunks
    [4CC gravado invertido][u32 little-endian: tamanho TOTAL do chunk][payload]
onde o tamanho inclui o próprio cabeçalho de 8 bytes. Alguns chunks são
containers (contêm subchunks); outros são folhas com dados binários.

Este script NÃO assume a semântica dos chunks — apenas percorre a árvore e
reporta identificadores, tamanhos e uma amostra do payload, para documentação
orientada por evidências.

Uso:
    python3 scripts/chunk_explorer.py extracted/GLBLDATA.PSX
    python3 scripts/chunk_explorer.py <arquivo> --max-depth 3 --sample 16
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

# 4CCs conhecidos: gravados invertidos no arquivo (little-endian de ASCII).
# Mapeamos o valor "invertido" -> nome legível.
KNOWN = {
    "LRTC": "CTRL",
    "COHS": "SHOC",
    "RDHS": "SHDR",
    "IPHS": "SHPI",   # EA image bank (hipótese)
    "LOOP": "POOL",
}

PRINTABLE = set(range(0x20, 0x7f))


def fourcc(b: bytes) -> str:
    return "".join(chr(c) if c in PRINTABLE else "." for c in b)


def looks_like_chunk_id(b: bytes) -> bool:
    return all((c in PRINTABLE) for c in b[:4])


def walk(data: bytes, base: int, end: int, depth: int, args, stats: Counter, out):
    off = base
    while off + 8 <= end:
        tag_raw = data[off:off + 4]
        size = int.from_bytes(data[off + 4:off + 8], "little")
        tag = fourcc(tag_raw)
        readable = KNOWN.get(tag, KNOWN.get(tag[::-1]))
        # sanidade: tamanho plausível
        if size < 8 or off + size > end:
            # não parece um chunk — provavelmente é payload de folha; encerra este nível
            return off
        stats[tag] += 1
        payload_off = off + 8
        payload_len = size - 8
        sample = data[payload_off:payload_off + args.sample]
        label = f"{tag}" + (f" ({readable})" if readable else "")
        indent = "  " * depth
        out.append(
            f"{indent}[{off:#08x}] {label:<16} size={size:>10}  "
            f"payload={payload_len:>10}  sample={sample.hex(' ')}  {fourcc(sample)}"
        )
        # tenta descer se o payload começar com algo que parece um sub-chunk
        if depth < args.max_depth and payload_len >= 8 and looks_like_chunk_id(data[payload_off:payload_off + 4]):
            sub_size = int.from_bytes(data[payload_off + 4:payload_off + 8], "little")
            if 8 <= sub_size <= payload_len:
                walk(data, payload_off, payload_off + payload_len, depth + 1, args, stats, out)
        off += size
    return off


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--max-depth", type=int, default=2)
    ap.add_argument("--sample", type=int, default=16)
    ap.add_argument("--limit", type=int, default=200, help="máx. de linhas de chunk a exibir")
    args = ap.parse_args()

    data = Path(args.file).read_bytes()
    out, stats = [], Counter()
    walk(data, 0, len(data), 0, args, stats, out)

    print(f"# {args.file}  ({len(data):,} bytes)")
    print(f"# chunks de topo/aninhados encontrados: {sum(stats.values())}")
    print("# contagem por identificador:")
    for tag, n in stats.most_common():
        readable = KNOWN.get(tag, KNOWN.get(tag[::-1]))
        print(f"#   {tag:<6} {('('+readable+')') if readable else '':<8} x{n}")
    print("#" + "-" * 70)
    for line in out[:args.limit]:
        print(line)
    if len(out) > args.limit:
        print(f"... (+{len(out)-args.limit} linhas omitidas)")


if __name__ == "__main__":
    main()

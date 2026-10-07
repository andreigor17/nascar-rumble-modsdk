#!/usr/bin/env python3
"""Inventory confirmed $gp-relative instructions by Ghidra function.

This is evidence for later object-level -G0/-G8 classification. A function with no
$gp-relative instruction is deliberately left unclassified: absence is not proof
that its original object used -G0.
"""

from __future__ import annotations

import argparse
import csv
import json
import struct
from pathlib import Path


LOAD_ADDRESS = 0x80010000
PAYLOAD_OFFSET = 0x800
GP = 0x800AF0E4
GP_OPS = {0x08, 0x09, *range(0x20, 0x2F)}


def render(exe_path: Path, functions_path: Path) -> str:
    exe = exe_path.read_bytes()
    entries = []
    total = 0
    with functions_path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            address = int(row["address"], 16)
            size = int(row["size"])
            if not LOAD_ADDRESS <= address < 0x800AF800:
                continue
            total += 1
            refs = []
            offset = PAYLOAD_OFFSET + address - LOAD_ADDRESS
            for instruction_offset in range(0, size, 4):
                word = struct.unpack_from("<I", exe, offset + instruction_offset)[0]
                opcode = word >> 26
                base = (word >> 21) & 0x1F
                if base == 28 and opcode in GP_OPS:
                    immediate = word & 0xFFFF
                    if immediate & 0x8000:
                        immediate -= 0x10000
                    refs.append(
                        {
                            "instruction": f"0x{address + instruction_offset:08X}",
                            "target": f"0x{GP + immediate:08X}",
                        }
                    )
            if refs:
                entries.append(
                    {
                        "address": f"0x{address:08X}",
                        "name": row["name"],
                        "size": size,
                        "references": refs,
                    }
                )

    data = {
        "schema_version": 1,
        "source": "ghidra_out/functions.csv + extracted/SLUS_010.68",
        "gp": f"0x{GP:08X}",
        "classification": {
            "uses_gp_relative": len(entries),
            "unclassified": total - len(entries),
            "total_functions": total,
        },
        "policy": (
            "uses_gp_relative is positive evidence for a -G-enabled object; functions "
            "without such an instruction remain unclassified until object boundaries are known"
        ),
        "functions": entries,
    }
    return json.dumps(data, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", type=Path, default=Path("extracted/SLUS_010.68"))
    parser.add_argument("--functions", type=Path, default=Path("ghidra_out/functions.csv"))
    parser.add_argument("--output", type=Path, default=Path("config/gp_usage.json"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = render(args.exe, args.functions)
    if args.check:
        if not args.output.is_file() or args.output.read_text() != generated:
            raise SystemExit(f"outdated generated file: {args.output}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(generated, encoding="utf-8", newline="\n")
    summary = json.loads(generated)["classification"]
    print(
        f"PASS — {summary['uses_gp_relative']} functions use $gp; "
        f"{summary['unclassified']} remain unclassified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

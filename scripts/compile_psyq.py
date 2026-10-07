#!/usr/bin/env python3
"""Compile one PsyQ C translation unit into a GNU MIPS ELF object via MASPSX."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--g-size", type=int, choices=(0, 8), default=0)
    parser.add_argument("--optimization", choices=("O1", "O2"), default="O2")
    args = parser.parse_args()

    wibo = ROOT / "tools/wibo/wibo"
    compiler = ROOT / "tools/psyq_sdk/psyq_4.3/bin/cc1psx.exe"
    maspsx = ROOT / "tools/maspsx/maspsx.py"
    for tool in (wibo, compiler, maspsx):
        if not tool.is_file():
            raise SystemExit(f"missing {tool}; run make setup-tools")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    raw_asm = args.output.with_suffix(".psyq.s")
    gnu_asm = args.output.with_suffix(".s")
    subprocess.run(
        [
            str(wibo),
            str(compiler),
            "-quiet",
            f"-{args.optimization}",
            f"-G{args.g_size}",
            "-g0",
            str(args.source),
            "-o",
            str(raw_asm),
        ],
        check=True,
    )

    maspsx_command = [
        "python3",
        str(maspsx),
        "--aspsx-version=2.56",
    ]
    if args.g_size:
        maspsx_command += ["--dont-force-G0", f"-G{args.g_size}"]
    with raw_asm.open("rb") as source, gnu_asm.open("wb") as output:
        subprocess.run(maspsx_command, stdin=source, stdout=output, check=True)

    subprocess.run(
        [
            "mipsel-linux-gnu-as",
            "-no-pad-sections",
            "-march=r3000",
            "-mabi=32",
            "-I",
            str(ROOT / "include"),
            "-o",
            str(args.output),
            str(gnu_asm),
        ],
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

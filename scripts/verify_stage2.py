#!/usr/bin/env python3
"""Validate the Stage 2 split, tool pins and byte-identical hybrid rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "extracted" / "SLUS_010.68"
REBUILD = ROOT / "build" / "SLUS_010.68"
EXPECTED_SHA256 = "e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75"
SYMBOL_PATTERN = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*) = (0x[0-9A-F]{8}); "
    r"// type:func size:(0x[0-9A-F]+) segment:main$"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL — {message}")


def tool_output(command: list[str]) -> str:
    return subprocess.run(command, check=True, text=True, capture_output=True).stdout


def expected_function_count() -> int:
    with (ROOT / "ghidra_out" / "functions.csv").open(newline="", encoding="utf-8") as source:
        return sum(
            1
            for row in csv.DictReader(source)
            if 0x80010000 <= int(row["address"], 16) < 0x800AF800
        )


def main() -> int:
    lock = json.loads((ROOT / "config" / "splat_toolchain.lock.json").read_text())
    splat_version = tool_output([str(ROOT / ".venv/bin/python"), "-m", "splat", "--version"])
    require(f"splat {lock['splat']['version']}" in splat_version, "unexpected Splat version")
    assembler_version = tool_output(["mipsel-linux-gnu-as", "--version"]).splitlines()[0]
    require(lock["binutils"]["version"] in assembler_version, "unexpected MIPS binutils version")

    symbols = []
    for line in (ROOT / "config" / "symbol_addrs.txt").read_text().splitlines():
        match = SYMBOL_PATTERN.fullmatch(line)
        if match:
            symbols.append(match.groups())
    require(len(symbols) == expected_function_count() == 1855, "incomplete Ghidra symbol import")
    require(len({name for name, _, _ in symbols}) == len(symbols), "duplicate function symbols")

    config = (ROOT / "config" / "splat.yaml").read_text()
    for fragment in (
        "start: 0x830",
        "vram: 0x80010030",
        "gp_value: 0x800AF0E4",
        "start: 0x9FD38, type: bss, vram: 0x800AF538",
        "bss_size: 0xD9B0",
    ):
        require(fragment in config, f"missing split invariant: {fragment}")

    for generated in (
        ROOT / "asm/main_0.s",
        ROOT / "asm/main_1.s",
        ROOT / "asm/data/main.rodata.s",
        ROOT / "asm/data/main.sdata.s",
        ROOT / "asm/data/main.data.s",
        ROOT / "linker/SLUS_010.68.ld",
    ):
        require(generated.is_file() and generated.stat().st_size > 0, f"missing {generated}")

    require(REFERENCE.is_file(), "missing extracted/SLUS_010.68")
    require(REBUILD.is_file(), "missing build/SLUS_010.68; run make build")
    require(REFERENCE.stat().st_size == REBUILD.stat().st_size == 0xA0000, "wrong EXE size")
    reference_hash = sha256(REFERENCE)
    rebuild_hash = sha256(REBUILD)
    require(reference_hash == EXPECTED_SHA256, "reference SHA-256 changed")
    require(rebuild_hash == reference_hash, "hybrid rebuild is not byte-identical")

    print(f"PASS — 1855 symbols; ASM/C/data coverage; SHA-256 {rebuild_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

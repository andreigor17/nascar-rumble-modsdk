#!/usr/bin/env python3
"""Validate the Stage 3 one-function workflow and its first integrated C match."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import function_tool


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL — {message}")


def main() -> int:
    lock = json.loads((ROOT / "config/decomp_tools.lock.json").read_text(encoding="utf-8"))
    for key, directory in (
        ("asm_differ", "asm-differ"),
        ("maspsx", "maspsx"),
        ("psyq_sdk", "psyq_sdk"),
    ):
        marker = ROOT / "tools" / directory / ".pinned-commit"
        require(marker.is_file(), f"missing pinned {directory}; run make setup-tools")
        require(marker.read_text().strip() == lock[key]["commit"], f"wrong {directory} commit")
    for tool in (ROOT / "tools/wibo/wibo", ROOT / "tools/objdiff/objdiff-cli"):
        require(tool.is_file(), f"missing {tool.relative_to(ROOT)}; run make setup-tools")

    exe = function_tool.Executable.read()
    functions = function_tool.read_functions(exe)
    rows = function_tool.build_backlog(exe, functions)
    require(len(rows) == 1855, "backlog does not cover all executable functions")
    with function_tool.BACKLOG_PATH.open(newline="", encoding="utf-8") as stream:
        stored = list(csv.DictReader(stream))
    require(rows == stored, "function backlog is stale; run make backlog")
    require(list(stored[0]) == function_tool.BACKLOG_FIELDS, "wrong backlog schema")

    pilot = next(row for row in rows if row["name"] == "FUN_80078c24")
    require(pilot["status"] == "matched", "pilot function is not marked matched")
    require(pilot["size"] == "36", "pilot function has the wrong size")
    require(pilot["callees"] == "FUN_800352f8", "pilot callee inventory changed")
    require(
        pilot["callers"] == "FUN_800524b4|FUN_80056c6c",
        "pilot caller inventory changed",
    )

    objects = function_tool.read_objects()
    metadata = objects.get("game/FUN_80078c24", {})
    source = ROOT / str(metadata.get("source", ""))
    built = ROOT / "build/src/game/FUN_80078c24.o"
    require(source.is_file(), "pilot C source is missing")
    require(built.is_file(), "pilot C object is missing; run make build")
    reference = (ROOT / "extracted/SLUS_010.68").read_bytes()
    rebuild = (ROOT / "build/SLUS_010.68").read_bytes()
    offset = 0x800 + int(str(metadata["address"]), 0) - exe.text_address
    size = int(metadata["size"])
    require(reference[offset : offset + size] == rebuild[offset : offset + size], "pilot mismatch")

    print(
        "PASS — one-command diff/context/progress backlog; "
        "FUN_80078c24 matched in C (36 bytes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

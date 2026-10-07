#!/usr/bin/env python3
"""Enforce the repository's dependency-free baseline formatting policy."""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {".c", ".h", ".py"}
VENDORED_TOOL_ROOTS = {
    ("tools", "asm-differ"),
    ("tools", "ghidra_extensions"),
    ("tools", "maspsx"),
    ("tools", "objdiff"),
    ("tools", "psyq_sdk"),
    ("tools", "RecompOne"),
    ("tools", "wibo"),
}


def is_generated(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return relative.parts[:1] == ("ghidra_out",) and (
        relative.name == "decomp_all.c" or relative.name.startswith("func_")
    )


def is_excluded(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return (
        any(part in {"node_modules", ".venv", ".venv-ghidra"} for part in relative.parts)
        or relative.parts[:2] in VENDORED_TOOL_ROOTS
        or is_generated(path)
    )


def source_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        names = result.stdout.splitlines()
    except (FileNotFoundError, subprocess.CalledProcessError):
        names = [str(path.relative_to(ROOT)) for path in ROOT.rglob("*") if path.is_file()]
    return sorted(
        ROOT / name
        for name in names
        if Path(name).suffix in SUFFIXES
        and not is_excluded(ROOT / name)
    )


def main() -> int:
    errors: list[str] = []
    for path in source_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        if not text.endswith("\n"):
            errors.append(f"{relative}: missing final newline")
        for number, line in enumerate(text.splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f"{relative}:{number}: trailing whitespace")
            if "\t" in line:
                errors.append(f"{relative}:{number}: tab indentation is not allowed")
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(relative))
            except SyntaxError as error:
                errors.append(f"{relative}:{error.lineno}: {error.msg}")
    if errors:
        print("Formatting check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS — formatting policy and Python syntax ({len(source_files())} source files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Prepara o RecompOne fixado, gera o C# e compila o host nativo."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from augment_recompone_funcmap import augment


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "config" / "recompone.lock.json"
TOOL = ROOT / "tools" / "RecompOne"
PATCH = ROOT / "recompone" / "patches" / "recompone-macos.patch"
MAP = ROOT / "recompone" / "nascar_funcmap.json"
GENERATED = ROOT / "recompone" / "Recompiled" / "main.cs"


def run(command: list[str], cwd: Path = ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def dotnet_path() -> str:
    configured = os.environ.get("RUMBLE_DOTNET")
    candidates = [configured, shutil.which("dotnet"), str(Path.home() / ".dotnet" / "dotnet")]
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        result = subprocess.run(
            [candidate, "--version"], text=True, capture_output=True, check=True
        )
        if result.stdout.strip().startswith("10."):
            return candidate
    raise SystemExit(".NET 10 SDK não encontrado; defina RUMBLE_DOTNET com o caminho correto")


def ensure_tool(lock: dict[str, object]) -> None:
    if not (TOOL / ".git").is_dir():
        run(["git", "clone", str(lock["repository"]), str(TOOL)])
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=TOOL, text=True, capture_output=True, check=True
    ).stdout.strip()
    if head != lock["commit"]:
        raise SystemExit(f"RecompOne em {head}; esperado {lock['commit']}")

    already_applied = subprocess.run(
        ["git", "apply", "--unidiff-zero", "--reverse", "--check", str(PATCH)],
        cwd=TOOL,
    ).returncode == 0
    if not already_applied:
        run(["git", "apply", "--unidiff-zero", "--check", str(PATCH)], cwd=TOOL)
        run(["git", "apply", "--unidiff-zero", str(PATCH)], cwd=TOOL)


def main() -> int:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    ensure_tool(lock)
    dotnet = dotnet_path()
    recompiler_project = TOOL / "RecompOne.Recompiler"
    recompiler = recompiler_project / "bin" / "Release" / "net10.0" / "recompone.dll"

    run([dotnet, "build", str(recompiler_project), "-c", "Release"])
    for _ in range(6):
        run([dotnet, str(recompiler), str(ROOT / "recompone" / "nascar.json")])
        if not augment(MAP, GENERATED):
            break
    else:
        raise SystemExit("funcMap do RecompOne não convergiu após seis passagens")
    run([dotnet, "build", str(ROOT / "recompone" / "host"), "-c", "Release"])
    print("PASS — NascarRumbleNative compilado para macOS arm64")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

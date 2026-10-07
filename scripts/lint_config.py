#!/usr/bin/env python3
"""Dependency-free lint for versioned decomp configs and lock manifests."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def walk_hashes(value: object, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key.endswith("sha256") and not HEX64.fullmatch(str(child)):
                errors.append(f"{child_path}: expected lowercase SHA-256")
            errors.extend(walk_hashes(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(walk_hashes(child, f"{path}[{index}]"))
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted((ROOT / "config").glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
            continue
        if not isinstance(payload, (dict, list)):
            errors.append(f"{path.relative_to(ROOT)}: top-level value must be object or array")
        errors.extend(
            f"{path.relative_to(ROOT)}:{error}" for error in walk_hashes(payload)
        )

    with (ROOT / "config/function_backlog.csv").open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
    required = {"address", "name", "size", "status", "owner", "scratch"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        errors.append("config/function_backlog.csv: incomplete schema")
    if len(rows) != len({row["name"] for row in rows}):
        errors.append("config/function_backlog.csv: duplicate function names")

    splat = (ROOT / "config/splat.yaml").read_text(encoding="utf-8")
    for fragment in ("target_path:", "platform: psx", "segments:", "type: bss"):
        if fragment not in splat:
            errors.append(f"config/splat.yaml: missing {fragment}")
    if "\t" in splat:
        errors.append("config/splat.yaml: tabs are not allowed")

    if errors:
        print("Configuration lint failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("PASS — JSON locks, backlog schema, checksums, and Splat invariants are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

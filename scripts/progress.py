#!/usr/bin/env python3
"""Generate, validate, compare, and summarize the canonical decomp progress report."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "config/function_backlog.csv"
OBJECTS = ROOT / "config/decomp_objects.json"
SETTINGS = ROOT / "config/progress_config.json"
BASELINE = ROOT / "config/progress_baseline.json"
SYMBOLS = ROOT / "config/symbol_addrs.txt"
OUTPUT = ROOT / "progress.json"
SYMBOL_PATTERN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*0x[0-9A-Fa-f]+;")
AUTO_SYMBOL_PATTERN = re.compile(r"^FUN_[0-9A-Fa-f]+$")


def percentage(part: int, total: int) -> float:
    return round(100 * part / total, 6) if total else 0.0


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def read_backlog() -> list[dict[str, str]]:
    with BACKLOG.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or len({row["name"] for row in rows}) != len(rows):
        raise ValueError("function backlog is empty or contains duplicate names")
    return rows


def data_metrics(settings: dict[str, Any]) -> dict[str, Any]:
    sections = []
    for section in settings["data_sections"]:
        size = int(section["end"]) - int(section["start"])
        if size < 0:
            raise ValueError(f"negative data section size: {section['name']}")
        matched = size if section["status"] == "matched" else 0
        sections.append(
            {
                "name": section["name"],
                "total_bytes": size,
                "matched_bytes": matched,
                "percent": percentage(matched, size),
            }
        )
    total = sum(item["total_bytes"] for item in sections)
    matched = sum(item["matched_bytes"] for item in sections)
    return {
        "matched_bytes": matched,
        "total_bytes": total,
        "percent": percentage(matched, total),
        "sections": sections,
    }


def subsystem_metrics(
    rows: list[dict[str, str]], settings: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    by_name = {row["name"]: row for row in rows}
    assigned: set[str] = set()
    result: dict[str, dict[str, Any]] = {}
    for key, subsystem in settings["subsystems"].items():
        names = subsystem["functions"]
        missing = sorted(set(names) - set(by_name))
        if missing:
            raise ValueError(f"unknown functions in subsystem {key}: {', '.join(missing)}")
        overlap = assigned.intersection(names)
        if overlap:
            raise ValueError(f"functions assigned to multiple subsystems: {', '.join(overlap)}")
        assigned.update(names)
        members = [by_name[name] for name in names]
        matched = [row for row in members if row["status"] == "matched"]
        total_bytes = sum(int(row["size"]) for row in members)
        matched_bytes = sum(int(row["size"]) for row in matched)
        result[key] = {
            "label": subsystem["label"],
            "functions_matched": len(matched),
            "functions_total": len(members),
            "code_matched_bytes": matched_bytes,
            "code_total_bytes": total_bytes,
            "percent": percentage(matched_bytes, total_bytes),
        }

    remaining = [row for row in rows if row["name"] not in assigned]
    matched = [row for row in remaining if row["status"] == "matched"]
    total_bytes = sum(int(row["size"]) for row in remaining)
    matched_bytes = sum(int(row["size"]) for row in matched)
    result["unclassified"] = {
        "label": "Unclassified",
        "functions_matched": len(matched),
        "functions_total": len(remaining),
        "code_matched_bytes": matched_bytes,
        "code_total_bytes": total_bytes,
        "percent": percentage(matched_bytes, total_bytes),
    }
    return result


def generate() -> dict[str, Any]:
    rows = read_backlog()
    settings = read_json(SETTINGS)
    objects = read_json(OBJECTS)["objects"]
    object_functions = {Path(item["source"]).stem: item for item in objects.values()}
    for row in rows:
        registered = object_functions.get(row["name"])
        expected_status = registered.get("status") if registered else "asm"
        if row["status"] != expected_status:
            raise ValueError(
                f"stale backlog status for {row['name']}: {row['status']} != {expected_status}"
            )

    total_code = sum(int(row["size"]) for row in rows)
    matched_rows = [row for row in rows if row["status"] == "matched"]
    matched_code = sum(int(row["size"]) for row in matched_rows)
    envelope = settings["code_envelope"]
    envelope_bytes = int(envelope["end"]) - int(envelope["start"])
    if total_code > envelope_bytes:
        raise ValueError("detected function bytes exceed the configured code envelope")

    symbol_names = []
    for line in SYMBOLS.read_text(encoding="utf-8").splitlines():
        if match := SYMBOL_PATTERN.match(line):
            symbol_names.append(match.group(1))
    if len(symbol_names) != len(set(symbol_names)):
        raise ValueError("duplicate symbols in config/symbol_addrs.txt")

    data = data_metrics(settings)
    return {
        "schema_version": 1,
        "target": settings["target"],
        "code": {
            "matched_bytes": matched_code,
            "total_function_bytes": total_code,
            "percent": percentage(matched_code, total_code),
            "envelope_bytes": envelope_bytes,
            "unclassified_envelope_bytes": envelope_bytes - total_code,
        },
        "functions": {
            "matched": len(matched_rows),
            "total": len(rows),
            "percent": percentage(len(matched_rows), len(rows)),
        },
        "data": data,
        "assembly": {
            "function_bytes_remaining": total_code - matched_code,
            "functions_remaining": len(rows) - len(matched_rows),
        },
        "symbols": {
            "total": len(symbol_names),
            "descriptive": sum(not AUTO_SYMBOL_PATTERN.match(name) for name in symbol_names),
            "auto_address": sum(bool(AUTO_SYMBOL_PATTERN.match(name)) for name in symbol_names),
        },
        "subsystems": subsystem_metrics(rows, settings),
        "build": settings["last_verified_build"],
    }


def serialized(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def flattened(report: dict[str, Any]) -> dict[str, int]:
    return {
        "code_matched_bytes": int(report["code"]["matched_bytes"]),
        "functions_matched": int(report["functions"]["matched"]),
        "data_matched_bytes": int(report["data"]["matched_bytes"]),
        "symbols_total": int(report["symbols"]["total"]),
        "asm_function_bytes_remaining": int(report["assembly"]["function_bytes_remaining"]),
    }


def check_baseline(report: dict[str, Any], baseline_path: Path = BASELINE) -> None:
    baseline = read_json(baseline_path)
    values = flattened(report)
    errors = []
    for key, expected in baseline["minimum"].items():
        if values[key] < int(expected):
            errors.append(f"{key} regressed: {values[key]} < {expected}")
    for key, expected in baseline["maximum"].items():
        if values[key] > int(expected):
            errors.append(f"{key} regressed: {values[key]} > {expected}")
    if errors:
        raise ValueError("; ".join(errors))


def summary(report: dict[str, Any]) -> str:
    code = report["code"]
    functions = report["functions"]
    data = report["data"]
    assembly = report["assembly"]
    symbols = report["symbols"]
    lines = [
        f"Code matched: {code['matched_bytes']}/{code['total_function_bytes']} bytes "
        f"({code['percent']:.3f}%)",
        f"Functions matched: {functions['matched']}/{functions['total']} "
        f"({functions['percent']:.3f}%)",
        f"Data matched: {data['matched_bytes']}/{data['total_bytes']} bytes "
        f"({data['percent']:.3f}%)",
        f"ASM function bytes remaining: {assembly['function_bytes_remaining']}",
        f"Symbols: {symbols['total']} total; {symbols['descriptive']} descriptive; "
        f"{symbols['auto_address']} address-based",
    ]
    return "\n".join(lines)


def comparison(current: dict[str, Any], previous: dict[str, Any]) -> str:
    now = flattened(current)
    before = flattened(previous)
    labels = {
        "code_matched_bytes": "Code matched bytes",
        "functions_matched": "Functions matched",
        "data_matched_bytes": "Data matched bytes",
        "asm_function_bytes_remaining": "ASM function bytes remaining",
        "symbols_total": "Symbols",
    }
    lines = ["| Metric | Base | Current | Delta |", "|---|---:|---:|---:|"]
    for key, label in labels.items():
        delta = now[key] - before[key]
        lines.append(f"| {label} | {before[key]} | {now[key]} | {delta:+d} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("write")
    subparsers.add_parser("check")
    subparsers.add_parser("summary")
    compare = subparsers.add_parser("compare")
    compare.add_argument("previous", type=Path)
    compare.add_argument("--github-summary", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = generate()
    if args.command == "write":
        OUTPUT.write_text(serialized(report), encoding="utf-8")
        check_baseline(report)
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    elif args.command == "check":
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != serialized(report):
            raise ValueError("progress.json is stale; run make progress-write")
        check_baseline(report)
        print("PASS — progress.json is current and the progress baseline did not regress")
    elif args.command == "summary":
        print(summary(report))
    else:
        previous = read_json(args.previous)
        table = comparison(report, previous)
        print(table)
        if args.github_summary and (destination := os.environ.get("GITHUB_STEP_SUMMARY")):
            with Path(destination).open("a", encoding="utf-8") as stream:
                stream.write("## Decompilation progress\n\n" + table + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, TypeError, ValueError) as error:
        print(f"FAIL — {error}", file=sys.stderr)
        raise SystemExit(1) from error

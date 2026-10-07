#!/usr/bin/env python3
"""Backlog, context, progress, and structural diff helpers for one-function work."""

from __future__ import annotations

import argparse
import csv
import json
import re
import struct
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXE_PATH = ROOT / "extracted" / "SLUS_010.68"
FUNCTIONS_PATH = ROOT / "ghidra_out" / "functions.csv"
STRINGS_PATH = ROOT / "ghidra_out" / "strings_xref.csv"
DECOMP_PATH = ROOT / "ghidra_out" / "decomp_all.c"
OBJECTS_PATH = ROOT / "config" / "decomp_objects.json"
BACKLOG_PATH = ROOT / "config" / "function_backlog.csv"
HEADER_SIZE = 0x800
BACKLOG_FIELDS = [
    "address",
    "name",
    "size",
    "instructions",
    "callers",
    "callees",
    "strings",
    "gp_relative",
    "status",
    "owner",
    "scratch",
]


@dataclass(frozen=True)
class Function:
    address: int
    name: str
    size: int

    @property
    def end(self) -> int:
        return self.address + self.size


@dataclass(frozen=True)
class Executable:
    data: bytes
    text_address: int
    text_size: int

    @classmethod
    def read(cls, path: Path = EXE_PATH) -> "Executable":
        data = path.read_bytes()
        if len(data) < HEADER_SIZE or data[:8] != b"PS-X EXE":
            raise SystemExit(f"invalid PS-X EXE: {path}")
        text_address, text_size = struct.unpack_from("<2I", data, 0x18)
        return cls(data, text_address, text_size)

    def bytes_at(self, address: int, size: int) -> bytes:
        offset = HEADER_SIZE + address - self.text_address
        if offset < HEADER_SIZE or offset + size > HEADER_SIZE + self.text_size:
            raise ValueError(f"range outside executable: 0x{address:08x}+0x{size:x}")
        return self.data[offset : offset + size]


def read_functions(exe: Executable) -> list[Function]:
    functions: list[Function] = []
    with FUNCTIONS_PATH.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            address = int(row["address"], 0)
            size = int(row["size"], 0)
            if exe.text_address <= address < exe.text_address + exe.text_size and size > 0:
                functions.append(Function(address, row["name"], size))
    return sorted(functions, key=lambda item: item.address)


def read_objects() -> dict[str, dict[str, object]]:
    payload = json.loads(OBJECTS_PATH.read_text(encoding="utf-8"))
    return payload["objects"]


def resolve_function(query: str, functions: list[Function]) -> Function:
    normalized = query.lower()
    try:
        address = int(normalized, 0 if normalized.startswith("0x") else 16)
    except ValueError:
        address = -1
    matches = [item for item in functions if item.name == query or item.address == address]
    if len(matches) != 1:
        raise SystemExit(f"function not found or ambiguous: {query}")
    return matches[0]


def display_target(address: int, names: dict[int, str]) -> str:
    return names.get(address, f"0x{address:08X}")


def call_graph(
    exe: Executable, functions: list[Function]
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    names = {item.address: item.name for item in functions}
    callers: dict[str, set[str]] = defaultdict(set)
    callees: dict[str, set[str]] = defaultdict(set)
    for function in functions:
        body = exe.bytes_at(function.address, function.size - function.size % 4)
        for offset in range(0, len(body), 4):
            word = struct.unpack_from("<I", body, offset)[0]
            if word >> 26 != 3:
                continue
            pc = function.address + offset
            target = ((pc + 4) & 0xF0000000) | ((word & 0x03FFFFFF) << 2)
            target_name = display_target(target, names)
            callees[function.name].add(target_name)
            if target in names:
                callers[names[target]].add(function.name)
    return (
        {name: sorted(values) for name, values in callers.items()},
        {name: sorted(values) for name, values in callees.items()},
    )


def string_map() -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    with STRINGS_PATH.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            name = row["in_function"].strip()
            value = row["text"].replace("\r", "\\r").replace("\n", "\\n")
            if name and value not in result[name]:
                result[name].append(value)
    return dict(result)


def gp_relative_names() -> set[str]:
    path = ROOT / "config" / "gp_usage.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        records = payload
    else:
        records = payload.get("functions", payload.get("entries", []))
    result: set[str] = set()
    for item in records:
        if isinstance(item, str):
            result.add(item)
        elif "references" in item or item.get("uses_gp") or item.get("gp_relative"):
            result.add(str(item.get("name")))
    return result


def existing_workflow_fields() -> dict[str, dict[str, str]]:
    if not BACKLOG_PATH.is_file():
        return {}
    with BACKLOG_PATH.open(newline="", encoding="utf-8") as stream:
        return {
            row["name"]: {key: row.get(key, "") for key in ("status", "owner", "scratch")}
            for row in csv.DictReader(stream)
        }


def object_by_function() -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for object_name, metadata in read_objects().items():
        name = Path(str(metadata["source"])).stem
        result[name] = {**metadata, "object": object_name}
    return result


def build_backlog(exe: Executable, functions: list[Function]) -> list[dict[str, str]]:
    callers, callees = call_graph(exe, functions)
    strings = string_map()
    gp_names = gp_relative_names()
    existing = existing_workflow_fields()
    objects = object_by_function()
    rows: list[dict[str, str]] = []
    for function in functions:
        prior = existing.get(function.name, {})
        object_metadata = objects.get(function.name, {})
        status = str(object_metadata.get("status", prior.get("status", "asm")))
        rows.append(
            {
                "address": f"0x{function.address:08X}",
                "name": function.name,
                "size": str(function.size),
                "instructions": str((function.size + 3) // 4),
                "callers": "|".join(callers.get(function.name, [])),
                "callees": "|".join(callees.get(function.name, [])),
                "strings": "|".join(strings.get(function.name, [])),
                "gp_relative": "yes" if function.name in gp_names else "no",
                "status": status,
                "owner": prior.get("owner", ""),
                "scratch": prior.get("scratch", ""),
            }
        )
    return rows


def write_backlog(rows: list[dict[str, str]]) -> None:
    with BACKLOG_PATH.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=BACKLOG_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} functions to {BACKLOG_PATH.relative_to(ROOT)}")


def extract_decompilation(function: Function) -> str:
    if not DECOMP_PATH.is_file():
        return (
            f"/* No local Ghidra export for {function.name}. "
            "The target assembly and call metadata remain complete. */\n"
        )
    text = DECOMP_PATH.read_text(encoding="utf-8", errors="replace")
    marker = re.compile(
        rf"^/\* ===== 0x{function.address:08x}\s+{re.escape(function.name)} ===== \*/$",
        re.MULTILINE,
    )
    match = marker.search(text)
    if not match:
        return f"/* No Ghidra decompilation exported for {function.name}. */\n"
    next_marker = text.find("/* ===== 0x", match.end())
    return text[match.start() : next_marker if next_marker >= 0 else len(text)].rstrip() + "\n"


def disassemble(target: Path, address: int) -> str:
    command = [
        "mipsel-linux-gnu-objdump",
        "-D",
        "-b",
        "binary",
        "-m",
        "mips:3000",
        "-EL",
        f"--adjust-vma=0x{address:x}",
        str(target),
    ]
    return subprocess.run(command, check=True, text=True, capture_output=True).stdout


def make_context(
    exe: Executable, functions: list[Function], function: Function
) -> Path:
    callers, callees = call_graph(exe, functions)
    strings = string_map()
    destination = ROOT / "scratch" / function.name
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "target.bin"
    target.write_bytes(exe.bytes_at(function.address, function.size))
    assembly = disassemble(target, function.address)
    (destination / "target.s").write_text(assembly, encoding="utf-8")
    metadata = {
        **asdict(function),
        "address": f"0x{function.address:08X}",
        "instructions": (function.size + 3) // 4,
        "callers": callers.get(function.name, []),
        "callees": callees.get(function.name, []),
        "strings": strings.get(function.name, []),
    }
    (destination / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    notes = [
        f"/* decomp.me context for {function.name}",
        f" * address: 0x{function.address:08X}; size: {function.size} bytes",
        f" * callers: {', '.join(metadata['callers']) or '(none found)'}",
        f" * callees: {', '.join(metadata['callees']) or '(none found)'}",
    ]
    for value in metadata["strings"]:
        notes.append(f" * string: {value}")
    notes.extend([" */", "", extract_decompilation(function)])
    (destination / "context.c").write_text("\n".join(notes), encoding="utf-8")
    print(f"Context ready: {destination.relative_to(ROOT)}/")
    return destination


def progress(rows: list[dict[str, str]]) -> None:
    total_functions = len(rows)
    total_bytes = sum(int(row["size"]) for row in rows)
    matched = [row for row in rows if row["status"] == "matched"]
    matched_bytes = sum(int(row["size"]) for row in matched)
    function_percent = 100 * len(matched) / total_functions if total_functions else 0
    byte_percent = 100 * matched_bytes / total_bytes if total_bytes else 0
    print(f"Functions matched: {len(matched)}/{total_functions} ({function_percent:.3f}%)")
    print(f"Code bytes matched: {matched_bytes}/{total_bytes} ({byte_percent:.3f}%)")
    candidates = [
        row
        for row in rows
        if row["status"] == "asm"
        and 20 <= int(row["instructions"]) <= 150
        and not row["callees"]
    ][:10]
    if candidates:
        print("Next leaf candidates (20-150 instructions):")
        for row in candidates:
            print(f"  {row['name']} @ {row['address']} — {row['instructions']} instructions")


def run_objdiff(exe: Executable, functions: list[Function], function: Function) -> None:
    metadata = object_by_function().get(function.name)
    if not metadata:
        raise SystemExit(f"no C object registered for {function.name}")
    candidate = ROOT / "build" / Path(str(metadata["source"])).with_suffix(".o")
    if not candidate.is_file():
        raise SystemExit(f"candidate object missing; run make build: {candidate}")
    context_dir = make_context(exe, functions, function)
    target_asm = context_dir / "target_obj.s"
    names = {item.address: item.name for item in functions}
    body = exe.bytes_at(function.address, function.size)
    source = [
        ".set noat",
        ".set noreorder",
        ".section .text",
        f".globl {function.name}",
        f".type {function.name}, @function",
        f"{function.name}:",
    ]
    for offset in range(0, len(body), 4):
        word = struct.unpack_from("<I", body, offset)[0]
        opcode = word >> 26
        pc = function.address + offset
        target_address = ((pc + 4) & 0xF0000000) | ((word & 0x03FFFFFF) << 2)
        if opcode in (2, 3) and target_address in names:
            source.append(f"{'j' if opcode == 2 else 'jal'} {names[target_address]}")
        else:
            source.append(f".word 0x{word:08x}")
    target_asm.write_text("\n".join(source) + "\n", encoding="utf-8")
    target_object = context_dir / "target.o"
    subprocess.run(
        [
            "mipsel-linux-gnu-as",
            "-no-pad-sections",
            "-march=r3000",
            "-mabi=32",
            "-o",
            str(target_object),
            str(target_asm),
        ],
        check=True,
    )
    report_path = context_dir / "objdiff.json"
    command = [
        str(ROOT / "tools" / "objdiff" / "objdiff-cli"),
        "diff",
        "-1",
        str(target_object),
        "-2",
        str(candidate),
        "-o",
        str(report_path),
        "--format",
        "json-pretty",
        function.name,
    ]
    result = subprocess.run(command)
    if result.returncode:
        raise SystemExit(result.returncode)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    symbols = report.get("left", {}).get("symbols", [])
    symbol = next((item for item in symbols if item.get("name") == function.name), {})
    percent = symbol.get("match_percent", "unknown")
    print(
        f"Objdiff {function.name}: {percent}% structural match; "
        f"report: {report_path.relative_to(ROOT)}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("backlog")
    subparsers.add_parser("progress")
    for command in ("context", "objdiff"):
        child = subparsers.add_parser(command)
        child.add_argument("function")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    exe = Executable.read()
    functions = read_functions(exe)
    rows = build_backlog(exe, functions)
    if args.command == "backlog":
        write_backlog(rows)
    elif args.command == "progress":
        progress(rows)
    else:
        function = resolve_function(args.function, functions)
        if args.command == "context":
            make_context(exe, functions, function)
        else:
            run_objdiff(exe, functions, function)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(f"command failed ({error.returncode}): {' '.join(error.cmd)}", file=sys.stderr)
        raise SystemExit(error.returncode) from error

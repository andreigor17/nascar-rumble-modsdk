#!/usr/bin/env python3
"""Compila o corpus mínimo com PsyQ 4.3/4.4 e compara bytes com o EXE."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _obj_functions(path: Path) -> dict[str, bytes]:
    data = path.read_bytes()
    if data[:4] != b"LNK\x02":
        raise ValueError(f"{path}: objeto PsyQ inválido")
    pos, current, text = 4, None, None
    blocks: list[tuple[int, bytes]] = []
    xdefs: list[tuple[int, str]] = []
    cursor = 0

    def u8():
        nonlocal pos
        value = data[pos]; pos += 1; return value

    def u16():
        nonlocal pos
        value = struct.unpack_from("<H", data, pos)[0]; pos += 2; return value

    def u32():
        nonlocal pos
        value = struct.unpack_from("<I", data, pos)[0]; pos += 4; return value

    def skip_patch():
        nonlocal pos
        kind = u8()
        if kind == 0: pos += 4
        elif kind in range(0, 25, 2): pos += 2
        else: skip_patch(); skip_patch()

    while pos < len(data):
        command = u8()
        if command == 0: break
        if command == 2:
            length = u16(); code = data[pos:pos + length]; pos += length
            if current == text: blocks.append((cursor, code)); cursor += length
        elif command == 6: current = u16()
        elif command == 8: pos += 4
        elif command == 10: pos += 3; skip_patch()
        elif command == 12:
            pos += 2; section = u16(); offset = u32(); length = u8()
            name = data[pos:pos + length].decode(); pos += length
            if section == text: xdefs.append((offset, name))
        elif command in (14, 28):
            pos += 2; pos += 1 + data[pos]
        elif command == 16:
            section = u16(); pos += 3; length = u8(); name = data[pos:pos + length]; pos += length
            if name.endswith(b".text"): text = section
        elif command == 18:
            pos += 6; pos += 1 + data[pos]
        elif command == 20:
            pos += 3; pos += 1 + data[pos]
        elif command == 46: pos += 1
        elif command == 48:
            pos += 8; pos += 1 + data[pos]
        elif command == 50: pos += 2
        elif command == 52: pos += 3
        elif command == 54: pos += 4
        elif command == 56: pos += 6
        elif command == 58: pos += 8
        elif command == 60: pos += 2
        elif command == 74:
            pos += 34; pos += 1 + data[pos]
        elif command in (76, 78, 80): pos += 10
        elif command == 82:
            pos += 14; pos += 1 + data[pos]
        else:
            raise ValueError(f"{path}: opcode LNK desconhecido {command} em 0x{pos - 1:x}")

    joined = b"".join(code for _, code in blocks)
    ordered = sorted(xdefs)
    return {
        name: joined[offset:(ordered[index + 1][0] if index + 1 < len(ordered) else len(joined))]
        for index, (offset, name) in enumerate(ordered)
    }


def exe_bytes(address: int, size: int) -> bytes:
    exe = (REPO / "extracted" / "SLUS_010.68").read_bytes()
    load = struct.unpack_from("<I", exe, 0x18)[0]
    offset = 0x800 + address - load
    return exe[offset:offset + size]


def run(
    sdk_root: Path,
    wibo: Path,
    version: str,
    optimization: str = "O2",
    g_size: int = 0,
) -> dict[str, bytes]:
    variant = version if (optimization, g_size) == ("O2", 0) else f"matrix-{version}-{optimization}-G{g_size}"
    build = REPO / "tools" / "compiler_probe" / "build" / variant
    build.mkdir(parents=True, exist_ok=True)
    source = REPO / "tools" / "compiler_probe" / "probe.c"
    compiler = sdk_root / f"psyq_{version}" / "bin" / "cc1psx.exe"
    assembler = sdk_root / "aspsx" / ("2.56" if version == "4.3" else "2.81") / "aspsx.exe"
    assembly, obj = build / "probe.s", build / "probe.obj"
    subprocess.run([
        str(wibo), str(compiler), "-quiet", f"-{optimization}", f"-G{g_size}", "-g0",
        str(source), "-o", str(assembly),
    ], check=True)
    command = [str(wibo), str(assembler)]
    if version == "4.4": command += ["-q", "-G", str(g_size)]
    command += [str(assembly), "-o", str(obj)]
    subprocess.run(command, check=True)
    return _obj_functions(obj)


def run_sensitive(sdk_root: Path, wibo: Path, version: str) -> bytes:
    build = REPO / "tools" / "compiler_probe" / "build" / version
    compiler = sdk_root / f"psyq_{version}" / "bin" / "cc1psx.exe"
    assembler_version = "2.56" if version == "4.3" else "2.81"
    assembler = sdk_root / "aspsx" / assembler_version / "aspsx.exe"
    linker = sdk_root / "psyq_4.4" / "bin" / "psylink.exe"
    source = REPO / "tools" / "compiler_probe" / "sensitive.c"
    assembly, obj = build / "sensitive.s", build / "sensitive.obj"
    binary, symbols, link_map = build / "sensitive.bin", build / "sensitive.sym", build / "sensitive.map"
    subprocess.run([str(wibo), str(compiler), "-quiet", "-O2", "-G0", "-g0", str(source), "-o", str(assembly)], check=True)
    subprocess.run([str(wibo), str(assembler), "-q", "-G", "0", str(assembly), "-o", str(obj)], check=True)
    suffix = version.replace(".", "")
    command_file = REPO / "tools" / "compiler_probe" / f"linker_sensitive_{suffix}.txt"
    output_spec = f"@{command_file.relative_to(REPO)},{binary.relative_to(REPO)},{symbols.relative_to(REPO)},{link_map.relative_to(REPO)}"
    subprocess.run([
        str(wibo), str(linker), "/c", "/p", "/n", "20", "/q",
        "/e", "probe_target=$800352F8", output_spec,
    ], check=True, cwd=REPO)
    return binary.read_bytes()


def verify_deterministic_link(sdk_root: Path, wibo: Path) -> str:
    build = REPO / "tools" / "compiler_probe" / "build" / "4.4"
    linker = sdk_root / "psyq_4.4" / "bin" / "psylink.exe"
    command_file = REPO / "tools" / "compiler_probe" / "linker_command.txt"
    cpe, symbols, link_map = build / "probe.cpe", build / "probe.sym", build / "probe.map"
    output_spec = f"@{command_file.relative_to(REPO)},{cpe.relative_to(REPO)},{symbols.relative_to(REPO)},{link_map.relative_to(REPO)}"
    command = [str(wibo), str(linker), "/c", "/n", "100", "/q", "/gp", ".sdata", "/m", output_spec]
    hashes = []
    for _ in range(2):
        subprocess.run(command, check=True, cwd=REPO)
        hashes.append(hashlib.sha256(cpe.read_bytes()).hexdigest())
    if hashes[0] != hashes[1]:
        raise RuntimeError("PSYLINK produziu CPE não determinístico")
    map_text = link_map.read_text(encoding="ascii", errors="replace")
    if "80010000 800100B7" not in map_text or "probe_empty" not in map_text:
        raise RuntimeError("mapa PSYLINK não contém layout/símbolos esperados")
    return hashes[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-root", required=True, type=Path)
    parser.add_argument("--wibo", required=True, type=Path)
    parser.add_argument("--matrix", action="store_true", help="também testa O1/O2 × G0/G8")
    args = parser.parse_args()
    corpus = json.loads((REPO / "config" / "compiler_corpus.json").read_text())
    probes = [
        item for item in corpus["functions"]
        if item.get("probe") and item["status"] != "matched-discriminator"
    ]
    failed = False
    for version in ("4.3", "4.4"):
        generated = run(args.sdk_root.resolve(), args.wibo.resolve(), version)
        matches = 0
        for item in probes:
            expected = exe_bytes(int(item["address"], 16), item["size"])
            actual = generated[item["probe"]]
            ok = actual == expected
            matches += ok
            print(f"PsyQ {version} {item['probe']}: {'MATCH' if ok else 'DIFF'}")
            failed |= item["status"] == "matched" and not ok
        print(f"PsyQ {version}: {matches}/{len(probes)} probes matched")
    if args.matrix:
        print("Matriz (inclui probes exploratórios):")
        for version in ("4.3", "4.4"):
            for optimization in ("O1", "O2"):
                for g_size in (0, 8):
                    generated = run(
                        args.sdk_root.resolve(), args.wibo.resolve(), version,
                        optimization=optimization, g_size=g_size,
                    )
                    count = sum(
                        generated[item["probe"]] == exe_bytes(int(item["address"], 16), item["size"])
                        for item in probes
                    )
                    print(f"  PsyQ {version} -{optimization} -G{g_size}: {count}/{len(probes)}")
    sensitive_expected = exe_bytes(0x80078C24, 36)
    sensitive_43 = run_sensitive(args.sdk_root.resolve(), args.wibo.resolve(), "4.3")
    sensitive_44 = run_sensitive(args.sdk_root.resolve(), args.wibo.resolve(), "4.4")
    print(f"PsyQ 4.3 probe sensível: {'MATCH' if sensitive_43 == sensitive_expected else 'DIFF'}")
    print(f"PsyQ 4.4 probe sensível: {'MATCH' if sensitive_44 == sensitive_expected else 'DIFF'}")
    failed |= sensitive_43 != sensitive_expected or sensitive_44 == sensitive_expected
    cpe_hash = verify_deterministic_link(args.sdk_root.resolve(), args.wibo.resolve())
    print(f"PSYLINK módulo mínimo: DETERMINÍSTICO sha256={cpe_hash}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())

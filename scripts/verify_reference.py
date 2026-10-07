#!/usr/bin/env python3
"""Verifica os dumps locais contra o manifesto versionado, sem modificar arquivos."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO / "config" / "reference_hashes.json"


def file_hashes(path: Path, chunk_size: int = 1024 * 1024) -> tuple[str, str]:
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            sha1.update(chunk)
            sha256.update(chunk)
    return sha1.hexdigest(), sha256.hexdigest()


def parse_psx_exe(path: Path) -> dict[str, int]:
    with path.open("rb") as stream:
        header = stream.read(0x800)
    if len(header) != 0x800 or header[:8] != b"PS-X EXE":
        raise ValueError("cabeçalho PS-X EXE inválido")
    pc0, gp0, text_address, text_size = struct.unpack_from("<4I", header, 0x10)
    stack_address = struct.unpack_from("<I", header, 0x30)[0]
    return {
        "pc0": pc0,
        "gp0": gp0,
        "text_address": text_address,
        "text_size": text_size,
        "stack_address": stack_address,
    }


def verify(root: Path, manifest_path: Path) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for artifact in manifest["artifacts"]:
        relative = Path(artifact["path"])
        path = root / relative
        if not path.is_file():
            errors.append(f"{relative}: arquivo ausente")
            continue
        size = path.stat().st_size
        if size != artifact["size"]:
            errors.append(f"{relative}: tamanho {size}, esperado {artifact['size']}")
        sha1, sha256 = file_hashes(path)
        if sha1 != artifact["sha1"]:
            errors.append(f"{relative}: SHA-1 {sha1}, esperado {artifact['sha1']}")
        if sha256 != artifact["sha256"]:
            errors.append(f"{relative}: SHA-256 {sha256}, esperado {artifact['sha256']}")
        if expected_header := artifact.get("psx_exe"):
            try:
                actual_header = parse_psx_exe(path)
            except ValueError as exc:
                errors.append(f"{relative}: {exc}")
                continue
            for field, expected_hex in expected_header.items():
                expected = int(expected_hex, 16)
                if actual_header[field] != expected:
                    errors.append(
                        f"{relative}: {field}=0x{actual_header[field]:08x}, esperado {expected_hex}"
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    errors = verify(args.root.resolve(), args.manifest.resolve())
    if errors:
        print("Referência inválida:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Referência válida: 3/3 artefatos, tamanhos, SHA-1, SHA-256 e PS-X EXE conferem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

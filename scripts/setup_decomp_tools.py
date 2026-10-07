#!/usr/bin/env python3
"""Install checksum-pinned local decompilation tools under tools/."""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
LOCK_PATH = ROOT / "config/decomp_tools.lock.json"


def host_key() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    aliases = {"amd64": "x86_64", "x86": "i686", "arm64": "arm64"}
    return f"{system}-{aliases.get(machine, machine)}"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url: str, expected: str, destination: Path) -> None:
    if destination.is_file() and digest(destination) == expected:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".download")
    with urllib.request.urlopen(url) as response, temporary.open("wb") as output:
        shutil.copyfileobj(response, output)
    actual = digest(temporary)
    if actual != expected:
        temporary.unlink(missing_ok=True)
        raise SystemExit(f"checksum mismatch for {url}: {actual}")
    temporary.replace(destination)


def install_archive(name: str, metadata: dict[str, str]) -> None:
    destination = TOOLS / name
    marker = destination / ".pinned-commit"
    if marker.is_file() and marker.read_text().strip() == metadata["commit"]:
        return
    if destination.exists():
        raise SystemExit(f"refusing to replace unrecognized tool directory: {destination}")
    with tempfile.TemporaryDirectory(prefix=f"rumble-{name}-") as temporary_dir:
        temporary = Path(temporary_dir)
        archive = temporary / f"{name}.tar.gz"
        download(metadata["archive_url"], metadata["archive_sha256"], archive)
        unpacked = temporary / "unpacked"
        unpacked.mkdir()
        with tarfile.open(archive) as source:
            source.extractall(unpacked, filter="data")
        roots = [item for item in unpacked.iterdir() if item.is_dir()]
        if len(roots) != 1:
            raise SystemExit(f"unexpected archive layout for {name}")
        shutil.move(str(roots[0]), destination)
    marker.write_text(metadata["commit"] + "\n", encoding="utf-8")


def install_binary(directory: str, filename: str, url: str, expected: str) -> Path:
    destination = TOOLS / directory / filename
    download(url, expected, destination)
    destination.chmod(destination.stat().st_mode | 0o111)
    return destination


def main() -> int:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    TOOLS.mkdir(exist_ok=True)
    archive_directories = {
        "asm_differ": "asm-differ",
        "maspsx": "maspsx",
        "psyq_sdk": "psyq_sdk",
    }
    for name, directory in archive_directories.items():
        install_archive(directory, lock[name])

    key = host_key()
    try:
        wibo_asset = lock["wibo"]["assets"][key]
        objdiff_name, objdiff_hash = lock["objdiff"]["assets"][key]
    except KeyError as error:
        raise SystemExit(f"unsupported host for decomp tools: {key}") from error

    wibo_url = lock["wibo"]["url_template"].format(name=wibo_asset["name"])
    install_binary("wibo", "wibo", wibo_url, wibo_asset["sha256"])
    objdiff_url = lock["objdiff"]["url_template"].format(name=objdiff_name)
    install_binary("objdiff", "objdiff-cli", objdiff_url, objdiff_hash)

    require = TOOLS / "asm-differ" / "diff.py"
    if not require.is_file():
        raise SystemExit(f"invalid asm-differ installation: {require}")

    print(
        f"PASS — asm-differ {lock['asm_differ']['commit'][:12]}, "
        f"MASPSX {lock['maspsx']['commit'][:12]}, objdiff {lock['objdiff']['version']}, "
        f"Wibo {lock['wibo']['version']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

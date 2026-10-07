#!/usr/bin/env python3
"""Valida a captura versionada do grid contra o catálogo de carros."""

from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CAPTURE = REPO / "experiments" / "grid" / "championship_gold_rush.json"


def load_names(path: Path) -> dict[int, str]:
    with path.open(newline="", encoding="utf-8") as stream:
        return {int(row["id"]): row["name"] for row in csv.DictReader(stream)}


def decode_grid(raw: bytes, count: int, entry_size: int = 8) -> list[dict[str, int | str]]:
    if not 1 <= count <= 8:
        raise ValueError(f"contagem implausível: {count}")
    if len(raw) < count * entry_size:
        raise ValueError("captura truncada")
    entries = []
    for index in range(count):
        entry = raw[index * entry_size : (index + 1) * entry_size]
        entries.append({
            "index": index,
            "kind": "PLAYER" if entry[1] == 0 else "AI",
            "model_id": entry[2],
            "position": entry[4],
        })
    return entries


def verify(capture_path: Path = DEFAULT_CAPTURE) -> list[str]:
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    raw = bytes.fromhex(capture["raw_hex"])
    count = raw[0]
    decoded = decode_grid(raw, count, capture["entry_size"])
    names = load_names(REPO / "docs" / "cars_wiki.csv")
    errors = []
    if len(decoded) != len(capture["expected"]):
        errors.append("quantidade de entradas diverge do esperado")
    for actual, expected in zip(decoded, capture["expected"]):
        actual["name"] = names.get(actual["model_id"], "?")
        if actual != expected:
            errors.append(f"entrada {actual['index']}: {actual!r} != {expected!r}")
    player_count = sum(entry["kind"] == "PLAYER" for entry in decoded)
    if player_count != 1:
        errors.append(f"esperado exatamente um jogador, obtido {player_count}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        print("Captura do grid inválida:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Captura do grid válida: 6/6 entradas, nomes, IDs, tipos e posições conferem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

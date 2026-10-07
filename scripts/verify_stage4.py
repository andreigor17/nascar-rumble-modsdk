#!/usr/bin/env python3
"""Validate Stage 4 metrics, local gates, and collaboration-governance artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import progress


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL — {message}")


def main() -> int:
    report = progress.generate()
    require(progress.OUTPUT.read_text(encoding="utf-8") == progress.serialized(report),
            "progress.json is stale")
    progress.check_baseline(report)
    require(report["functions"]["matched"] >= 1, "matched function metric is missing")
    require(report["code"]["matched_bytes"] >= 36, "matched code metric is missing")
    require(report["data"]["matched_bytes"] == 22852, "data metric changed unexpectedly")
    require(report["symbols"]["total"] == 1855, "symbol metric changed unexpectedly")
    require(report["build"]["status"] == "matching", "last verified build is not matching")
    for relative in (
        "CONTRIBUTING.md",
        "Dockerfile",
        ".github/pull_request_template.md",
    ):
        require((ROOT / relative).is_file(), f"missing governance artifact {relative}")
    json.loads((ROOT / "progress.json").read_text(encoding="utf-8"))
    print("PASS — canonical metrics, local gates, anti-regression, and governance are present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

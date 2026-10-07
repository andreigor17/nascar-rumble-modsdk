#!/usr/bin/env python3
"""Build and manually publish the static site to the gh-pages branch."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DIST = SITE / "dist"


def run(
    command: list[str],
    *,
    cwd: Path = ROOT,
    capture: bool = False,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=capture,
        input=input_text,
    )


def output(command: list[str], cwd: Path = ROOT) -> str:
    return run(command, cwd=cwd, capture=True).stdout.strip()


def clear_checkout(checkout: Path) -> None:
    """Remove only files inside the temporary checkout created by this script."""
    if (
        checkout.name != "publish"
        or not checkout.parent.name.startswith("rumble-site-")
        or not (checkout / ".git").exists()
    ):
        raise RuntimeError(f"diretório temporário inesperado: {checkout}")
    for child in checkout.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def configure_pages(repository: str) -> None:
    body = json.dumps(
        {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}
    )
    run(
        ["gh", "api", "--method", "PUT", f"repos/{repository}/pages", "--input", "-"],
        input_text=body,
    )
    print("GitHub Pages configurado para gh-pages / (root).")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publica site/dist na branch gh-pages sem GitHub Actions."
    )
    parser.add_argument(
        "--configure-pages",
        action="store_true",
        help="também troca a configuração do GitHub Pages para deploy por branch",
    )
    args = parser.parse_args()

    run(["npm", "ci"], cwd=SITE)
    run(["npm", "run", "build"], cwd=SITE)
    (DIST / ".nojekyll").write_text("Static site built locally.\n", encoding="utf-8")

    remote = output(["git", "remote", "get-url", "origin"])
    source = output(["git", "rev-parse", "--short", "HEAD"])
    repository = output(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]
    )
    branch_exists = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--heads", remote, "gh-pages"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0

    with tempfile.TemporaryDirectory(prefix="rumble-site-") as temporary:
        publish_root = Path(temporary) / "publish"
        if branch_exists:
            run(
                ["git", "clone", "--depth", "1", "--branch", "gh-pages", remote, str(publish_root)]
            )
        else:
            run(["git", "clone", "--depth", "1", remote, str(publish_root)])
            run(["git", "switch", "--orphan", "gh-pages"], cwd=publish_root)

        clear_checkout(publish_root)
        shutil.copytree(DIST, publish_root, dirs_exist_ok=True)
        run(["git", "add", "--all"], cwd=publish_root)
        unchanged = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=publish_root
        ).returncode == 0
        if unchanged:
            print("Site sem alterações; nada para publicar.")
        else:
            run(["git", "commit", "-m", f"Publish site from {source}"], cwd=publish_root)
            run(["git", "push", "origin", "gh-pages"], cwd=publish_root)
            print("Site enviado para a branch gh-pages.")

    if args.configure_pages:
        configure_pages(repository)
    else:
        print(
            "Se for a primeira publicação manual, rode novamente com --configure-pages "
            "ou selecione gh-pages / (root) em Settings > Pages."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

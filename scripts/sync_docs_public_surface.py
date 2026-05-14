"""
Sync public site files into docs for GitHub Pages.
"""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def copy_file(name: str) -> None:
    """Copy one top-level public file when present."""
    source = ROOT / name
    if source.is_file():
        shutil.copy2(source, DOCS / name)


def main() -> int:
    """Sync docs public surface."""
    try:
        DOCS.mkdir(parents=True, exist_ok=True)
        copy_file("index.html")
        copy_file("styles.css")
        copy_file("robots.txt")
        copy_file("sitemap.xml")
        copy_file("_headers")

        target_sites = DOCS / "sites"
        if target_sites.exists():
            shutil.rmtree(target_sites)

        shutil.copytree(ROOT / "sites", target_sites)
        target_assets = DOCS / "assets"
        if target_assets.exists():
            shutil.rmtree(target_assets)

        if (ROOT / "assets").exists():
            shutil.copytree(ROOT / "assets", target_assets)

        (DOCS / ".nojekyll").touch()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print("docs public surface synced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

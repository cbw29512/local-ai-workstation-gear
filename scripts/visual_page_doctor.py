"""
Validate visual styling on live affiliate pages.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
CSS_MARKER = "assets/styles/affiliate-page.css"
HERO_MARKER = 'data-ai-visual-hero="true"'


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    """Validate visual page state."""
    registry = load_json(REGISTRY)
    problems: list[str] = []
    checked = 0

    for row in registry.get("links", []):
        if row.get("approved_by_chris") is not True or row.get("live_enabled") is not True:
            continue

        checked += 1
        slug = str(row.get("slug", ""))
        path = ROOT / "sites" / slug / "index.html"

        if not path.is_file():
            problems.append(f"{slug}: missing page")
            continue

        text = path.read_text(encoding="utf-8", errors="replace")

        if CSS_MARKER not in text:
            problems.append(f"{slug}: missing shared CSS")

        if HERO_MARKER not in text:
            problems.append(f"{slug}: missing visual hero")

        if "<img" not in text.lower():
            problems.append(f"{slug}: missing image/visual element")

    print("RESULT:")

    if problems:
        print("VISUAL PAGE STATE: NEEDS REVIEW")
        print(f"checked_pages: {checked}")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("VISUAL PAGE STATE: PASS")
    print(f"checked_pages: {checked}")
    print("next_required_gate: browser_visual_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

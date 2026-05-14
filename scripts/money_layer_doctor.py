"""
Validate Amazon money layer.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
DOCS = ROOT / "docs"


def main() -> int:
    """Validate public money-layer state."""
    problems: list[str] = []

    if not REGISTRY.is_file():
        problems.append("missing Amazon link registry")
    else:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for link in data.get("links", []):
            if link.get("live_enabled") is True:
                if link.get("approved_by_chris") is not True:
                    problems.append(f"{link.get('slug')}: live without Chris approval")

    docs_html = list(DOCS.rglob("*.html"))

    if not docs_html:
        problems.append("docs HTML files missing")

    for path in docs_html:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "As an Amazon Associate I earn from qualifying purchases." not in text:
            problems.append(f"{path.relative_to(ROOT)} missing Amazon disclosure")

    print("RESULT:")

    if problems:
        print("MONEY LAYER STATE: NEEDS REVIEW")
        for problem in problems[:80]:
            print(f"- {problem}")
        return 1

    print("MONEY LAYER STATE: PASS")
    print("Amazon disclosure exists and live links require Chris approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

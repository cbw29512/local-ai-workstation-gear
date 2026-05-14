"""
Validate public render output.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "items.json"


def main() -> int:
    """Validate clean public render state."""
    inventory = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    items = inventory.get("items", [])
    site_pages = list((ROOT / "sites").glob("*/index.html"))

    wrong_hits = []
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or "reports" in path.parts:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        for bad in ["Home Depot Affiliate Engine", "homedepotaffiliate", "Home Depot"]:
            if bad in text:
                wrong_hits.append(f"{path.relative_to(ROOT)} :: {bad}")

    print("RESULT:")

    if len(items) != 24:
        print(f"PUBLIC RENDER STATE: NEEDS REVIEW - item count {len(items)}")
        return 1

    if len(site_pages) != 24:
        print(f"PUBLIC RENDER STATE: NEEDS REVIEW - site page count {len(site_pages)}")
        return 1

    if wrong_hits:
        print("PUBLIC RENDER STATE: NEEDS REVIEW - wrong branding")
        for hit in wrong_hits[:80]:
            print(f"- {hit}")
        return 1

    print("PUBLIC RENDER STATE: PASS")
    print("item_count: 24")
    print("site_page_count: 24")
    print("wrong_brand_hits: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

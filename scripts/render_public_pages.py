"""
Render public item-first pages from data/items.json.

State:
- data/items.json is source of truth.
- index.html is the funnel/controller.
- sites/<slug>/index.html are visitor-facing pages.

Safety:
- No fake prices, ratings, discounts, or affiliate claims.
- No git add, commit, push, GitHub API, or credentials.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from renderer.io import load_inventory, setup_logging
from renderer.site_writer import remove_legacy_public_surfaces, write_pages


def main() -> int:
    """Render clean public pages."""
    setup_logging()

    try:
        inventory = load_inventory()
        remove_legacy_public_surfaces()
        write_pages(inventory)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"items_rendered: {len(inventory['items'])}")
    print("legacy_public_surfaces_removed: pages,hubs,old sites")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Sync Amazon affiliate URL aliases in registry.

State:
- New generated links use affiliate_url.
- Older renderers may expect approved_affiliate_url.
- This sync keeps both fields aligned.

Safety:
- Registry field sync only.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON safely."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON safely."""
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    """Sync affiliate_url and approved_affiliate_url fields."""
    data = load_json(REGISTRY)
    changed = 0

    for row in data.get("links", []):
        affiliate_url = row.get("affiliate_url")
        approved_url = row.get("approved_affiliate_url")

        if affiliate_url and not approved_url:
            row["approved_affiliate_url"] = affiliate_url
            changed += 1

        if approved_url and not affiliate_url:
            row["affiliate_url"] = approved_url
            changed += 1

    write_json(REGISTRY, data)

    print("RESULT: PASS")
    print(f"aliases_synced: {changed}")
    print("next_required_gate: render_all_live_amazon_links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

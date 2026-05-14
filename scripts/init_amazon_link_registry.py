"""
Initialize Amazon affiliate link registry from Amazon-only research.

Safety:
- Creates placeholders only.
- Does not create affiliate links.
- Does not edit live product pages.
- Does not commit or push.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.amazon_links_io import load_json, write_json
from webmaster.amazon_links_paths import AMAZON_RESULTS, LINK_REGISTRY


PLACEHOLDER = "PASTE_CHRIS_APPROVED_AMAZON_AFFILIATE_URL_HERE"


def candidate_to_link(slot: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Convert one Amazon research candidate to locked link registry row."""
    return {
        "slot": slot["slot"],
        "slug": slot["slug"],
        "product_name": candidate["product_name"],
        "brand": candidate["brand"],
        "asin": candidate.get("asin", ""),
        "amazon_url": candidate["amazon_url"],
        "approved_affiliate_url": PLACEHOLDER,
        "approved_by_chris": False,
        "live_enabled": False,
        "button_text": "Check on Amazon",
        "first_added_to_registry_at": None,
        "last_affiliate_review_at": None,
    }


def build_registry() -> dict[str, Any]:
    """Build placeholder registry from Amazon-only candidates."""
    results = load_json(AMAZON_RESULTS)
    links = []

    for slot in results.get("slots", []):
        for candidate in slot.get("recommended_candidates", []):
            links.append(candidate_to_link(slot, candidate))

    return {
        "status": "awaiting_chris_approved_amazon_affiliate_links",
        "site": "Local AI Workstation Gear",
        "required_disclosure": "As an Amazon Associate I earn from qualifying purchases.",
        "rules": {
            "amazon_only": True,
            "approved_by_chris_required": True,
            "no_fake_prices": True,
            "no_fake_ratings": True,
            "no_fake_reviews": True,
            "no_fake_discounts": True
        },
        "links": links,
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": "paste_chris_approved_amazon_affiliate_links"
    }


def main() -> int:
    """Create placeholder Amazon link registry."""
    try:
        registry = build_registry()
        write_json(LINK_REGISTRY, registry)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"registry_links: {len(registry['links'])}")
    print(f"registry: {LINK_REGISTRY}")
    print("next_required_gate: paste_chris_approved_amazon_affiliate_links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

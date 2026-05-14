"""
Enable Chris-approved Amazon affiliate link for Slot 1.

State:
- Slot 1 becomes the first live Amazon affiliate product.
- The provided short amzn.to link is stored as pending manual mapping.
- No prices, ratings, reviews, or discounts are added.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "amazon_links" / "approved_amazon_links.json"
LOG_FILE = ROOT / "logs" / "enable_first_approved_amazon_link.log"

APPROVED_URL = (
    "https://www.amazon.com/dp/B0GHNDHGP5?&linkCode=ll2&tag=maxyourheal06-20"
    "&linkId=b4acf159efe386fdf19ed4be0db83bf7&language=en_US&ref_=as_li_ss_tl"
)

PENDING_SHORT_URL = "https://amzn.to/42Dz8f1"


def setup_logging() -> None:
    """Create traceable logs for the approval action."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_registry() -> dict[str, Any]:
    """Load the Amazon link registry."""
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load registry: %s", exc)
        raise


def write_registry(registry: dict[str, Any]) -> None:
    """Write the Amazon link registry."""
    try:
        REGISTRY.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write registry: %s", exc)
        raise


def approved_target(now: str) -> dict[str, Any]:
    """Build the approved Slot 1 product record."""
    return {
        "slot": 1,
        "slug": "starter-local-ai-mini-pc",
        "product_name": "ACEMAGIC M1A PRO+ AI Mini Gaming PC",
        "brand": "ACEMAGIC",
        "asin": "B0GHNDHGP5",
        "amazon_url": "https://www.amazon.com/dp/B0GHNDHGP5",
        "approved_affiliate_url": APPROVED_URL,
        "approved_by_chris": True,
        "live_enabled": True,
        "button_text": "Check on Amazon",
        "first_added_to_registry_at": now,
        "last_affiliate_review_at": now,
        "notes": "Chris directly provided this Amazon Associates URL."
    }


def upsert_link(registry: dict[str, Any], target: dict[str, Any]) -> None:
    """Replace existing Slot 1 row or append a new one."""
    links = registry.setdefault("links", [])
    replaced = False

    for index, link in enumerate(links):
        same_slot = link.get("slot") == 1
        same_slug = link.get("slug") == "starter-local-ai-mini-pc"
        same_asin = link.get("asin") == "B0GHNDHGP5"

        if same_slot or same_slug or same_asin:
            links[index] = {**link, **target}
            replaced = True
            break

    if not replaced:
        links.append(target)


def store_pending_short_link(registry: dict[str, Any], now: str) -> None:
    """Keep the short link without making it live."""
    pending = registry.setdefault("pending_short_links", [])

    if not any(item.get("url") == PENDING_SHORT_URL for item in pending):
        pending.append(
            {
                "url": PENDING_SHORT_URL,
                "status": "pending_manual_product_mapping",
                "added_at": now,
                "reason": "Short link provided by Chris; product identity not mapped yet."
            }
        )


def main() -> int:
    """Enable the approved Amazon link."""
    setup_logging()

    try:
        registry = load_registry()
        now = datetime.now(timezone.utc).isoformat()

        upsert_link(registry, approved_target(now))
        store_pending_short_link(registry, now)

        registry["status"] = "has_chris_approved_live_amazon_links"
        registry["last_updated_at"] = now
        registry["affiliate_link_changes_allowed"] = False
        registry["product_swap_allowed"] = False
        registry["git_commit_allowed"] = False
        registry["git_push_allowed"] = False
        registry["publish_allowed"] = False
        registry["next_required_gate"] = "render_approved_amazon_links"

        write_registry(registry)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print("enabled_slug: starter-local-ai-mini-pc")
    print("enabled_asin: B0GHNDHGP5")
    print("next_required_gate: render_approved_amazon_links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

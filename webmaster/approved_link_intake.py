"""
Approved Amazon link intake helpers.

State schema:
{
  "slot": int,
  "slug": str,
  "product_name": str,
  "asin": str,
  "approved_affiliate_url": str,
  "approved_by_chris": true,
  "live_enabled": true
}

Safety:
- Amazon/amzn.to only.
- No fake prices, ratings, reviews, or discounts.
- No product swap execution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.amazon_links_io import load_json, write_json
from webmaster.amazon_links_paths import LINK_REGISTRY, ROOT
from webmaster.amazon_links_validate import is_amazon_url


INTAKE = ROOT / "data" / "amazon_links" / "next_approved_link.json"


def validate_intake(row: dict[str, Any]) -> list[str]:
    """Validate one approved Amazon intake row."""
    problems: list[str] = []

    required = [
        "slot",
        "slug",
        "product_name",
        "brand",
        "asin",
        "amazon_url",
        "approved_affiliate_url",
    ]

    for key in required:
        if not row.get(key):
            problems.append(f"{key} is required")

    if row.get("approved_by_chris") is not True:
        problems.append("approved_by_chris must be true")

    if row.get("live_enabled") is not True:
        problems.append("live_enabled must be true")

    if row.get("amazon_url") and not is_amazon_url(str(row["amazon_url"])):
        problems.append("amazon_url must be Amazon/amzn.to")

    affiliate_url = str(row.get("approved_affiliate_url", ""))

    if affiliate_url and not is_amazon_url(affiliate_url):
        problems.append("approved_affiliate_url must be Amazon/amzn.to")

    return problems


def build_registry_row(row: dict[str, Any]) -> dict[str, Any]:
    """Build registry row from approved intake."""
    now = datetime.now(timezone.utc).isoformat()

    return {
        "slot": row["slot"],
        "slug": row["slug"],
        "product_name": row["product_name"],
        "brand": row["brand"],
        "asin": row["asin"],
        "amazon_url": row["amazon_url"],
        "approved_affiliate_url": row["approved_affiliate_url"],
        "approved_by_chris": True,
        "live_enabled": True,
        "button_text": row.get("button_text") or "Check on Amazon",
        "first_added_to_registry_at": now,
        "last_affiliate_review_at": now,
        "notes": row.get("notes", "Chris-approved Amazon affiliate link."),
    }


def upsert_registry(row: dict[str, Any]) -> dict[str, Any]:
    """Upsert the approved link into the registry."""
    registry = load_json(LINK_REGISTRY)
    target = build_registry_row(row)
    links = registry.setdefault("links", [])
    replaced = False

    for index, existing in enumerate(links):
        same_slug = existing.get("slug") == target["slug"]
        same_asin = existing.get("asin") == target["asin"]

        if same_slug or same_asin:
            links[index] = {**existing, **target}
            replaced = True
            break

    if not replaced:
        links.append(target)

    registry["status"] = "has_chris_approved_live_amazon_links"
    registry["last_updated_at"] = datetime.now(timezone.utc).isoformat()
    registry["affiliate_link_changes_allowed"] = False
    registry["product_swap_allowed"] = False
    registry["git_commit_allowed"] = False
    registry["git_push_allowed"] = False
    registry["publish_allowed"] = False
    registry["next_required_gate"] = "render_approved_amazon_links"

    write_json(LINK_REGISTRY, registry)
    return target

"""
Build timestamped lifecycle records for item rotation.

Data schema per item:
{
  "slug": str,
  "first_seen_at": str,
  "next_review_at": str,
  "rotation_due_at": str,
  "rotation_status": str,
  "replacement_allowed": false
}
"""

from __future__ import annotations

from typing import Any

from webmaster.lifecycle_io import load_json
from webmaster.lifecycle_paths import ITEMS_JSON, LIFECYCLE_JSON, POLICY_JSON
from webmaster.time_utils import add_days_iso, utc_now_iso


def existing_by_slug() -> dict[str, dict[str, Any]]:
    """Preserve existing lifecycle timestamps when present."""
    if not LIFECYCLE_JSON.is_file():
        return {}

    lifecycle = load_json(LIFECYCLE_JSON)
    return {
        item["slug"]: item
        for item in lifecycle.get("items", [])
        if item.get("slug")
    }


def locked_flags() -> dict[str, bool]:
    """Return locked safety flags."""
    return {
        "replacement_allowed": False,
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }


def build_lifecycle_item(
    item: dict[str, Any],
    existing: dict[str, Any],
    policy: dict[str, Any],
    now: str,
) -> dict[str, Any]:
    """Build one lifecycle record."""
    first_seen = existing.get("first_seen_at") or now
    review_days = int(policy["review_cadence_days"])
    rotation_days = int(policy["default_rotation_window_days"])

    return {
        "slot": item["slot"],
        "slug": item["slug"],
        "title": item["title"],
        "category": item["category"],
        "status": existing.get("status", "testing"),
        "rotation_status": existing.get("rotation_status", "testing"),
        "first_seen_at": first_seen,
        "first_live_at": existing.get("first_live_at"),
        "last_reviewed_at": existing.get("last_reviewed_at") or now,
        "next_review_at": existing.get("next_review_at") or add_days_iso(now, review_days),
        "rotation_due_at": existing.get("rotation_due_at") or add_days_iso(first_seen, rotation_days),
        "last_optimized_at": existing.get("last_optimized_at"),
        "last_replaced_at": existing.get("last_replaced_at"),
        "protected_at": existing.get("protected_at"),
        "clicks_30d": existing.get("clicks_30d", 0),
        "affiliate_clicks_30d": existing.get("affiliate_clicks_30d", 0),
        "impressions_30d": existing.get("impressions_30d", 0),
        **locked_flags(),
    }


def build_lifecycle() -> dict[str, Any]:
    """Create the full lifecycle document."""
    inventory = load_json(ITEMS_JSON)
    policy = load_json(POLICY_JSON)
    old_items = existing_by_slug()
    now = utc_now_iso()

    items = [
        build_lifecycle_item(item, old_items.get(item["slug"], {}), policy, now)
        for item in inventory.get("items", [])
    ]

    return {
        "created_at": now,
        "updated_at": now,
        "status": "item_lifecycle_timestamped",
        "item_count": len(items),
        "rotation_policy": str(POLICY_JSON),
        "items": items,
        **locked_flags(),
        "next_required_gate": "lifecycle_timestamp_review",
    }

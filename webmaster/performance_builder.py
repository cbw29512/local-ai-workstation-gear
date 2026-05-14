"""
Build timestamped performance metric records.

All metrics default to zero until analytics/click tracking imports data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.performance_io import load_json, write_json
from webmaster.performance_paths import ITEMS_JSON, ITEM_PERFORMANCE_JSON


def utc_now_iso() -> str:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def existing_by_slug() -> dict[str, dict[str, Any]]:
    """Preserve existing performance metrics when present."""
    if not ITEM_PERFORMANCE_JSON.is_file():
        return {}

    data = load_json(ITEM_PERFORMANCE_JSON)
    return {item["slug"]: item for item in data.get("items", []) if item.get("slug")}


def build_item(item: dict[str, Any], existing: dict[str, Any], now: str) -> dict[str, Any]:
    """Build one performance record."""
    return {
        "slot": item["slot"],
        "slug": item["slug"],
        "title": item["title"],
        "category": item["category"],
        "clicks_30d": existing.get("clicks_30d", 0),
        "affiliate_clicks_30d": existing.get("affiliate_clicks_30d", 0),
        "impressions_30d": existing.get("impressions_30d", 0),
        "ctr_30d": existing.get("ctr_30d", 0.0),
        "last_metric_snapshot_at": existing.get("last_metric_snapshot_at") or now,
        "metric_source": existing.get("metric_source", "manual_or_future_analytics_import"),
        "replacement_allowed": False,
        "product_swap_allowed": False,
        "affiliate_link_changes_allowed": False,
    }


def build_performance() -> dict[str, Any]:
    """Build full performance document."""
    inventory = load_json(ITEMS_JSON)
    old = existing_by_slug()
    now = utc_now_iso()

    items = [
        build_item(item, old.get(item["slug"], {}), now)
        for item in inventory.get("items", [])
    ]

    return {
        "created_at": now,
        "updated_at": now,
        "status": "item_performance_timestamped",
        "item_count": len(items),
        "items": items,
        "replacement_allowed": False,
        "product_swap_allowed": False,
        "affiliate_link_changes_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }


def write_performance() -> dict[str, Any]:
    """Build and write performance metrics."""
    payload = build_performance()
    write_json(ITEM_PERFORMANCE_JSON, payload)
    return payload

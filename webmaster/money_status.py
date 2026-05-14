"""
Money status monitor for the local AI webmaster.

State:
- Reads Amazon link registry.
- Reads lifecycle and performance data.
- Reads manual Amazon metrics snapshot file.

Safety:
- Read-only.
- No affiliate link changes.
- No product swaps.
- No commits or pushes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.money_io import load_json
from webmaster.money_paths import LIFECYCLE, PERFORMANCE, REGISTRY, SNAPSHOTS
from webmaster.money_snapshot import snapshot_by_slug, snapshot_status


def live_links(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return Chris-approved live Amazon links."""
    return [
        link for link in registry.get("links", [])
        if link.get("approved_by_chris") is True
        and link.get("live_enabled") is True
    ]


def map_by_slug(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map item-style JSON records by slug."""
    return {
        item["slug"]: item
        for item in data.get("items", [])
        if item.get("slug")
    }


def build_live_item(
    link: dict[str, Any],
    lifecycle_map: dict[str, dict[str, Any]],
    performance_map: dict[str, dict[str, Any]],
    snapshot_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build one live money item row."""
    slug = link["slug"]
    performance = performance_map.get(slug, {})
    snapshot = snapshot_map.get(slug)

    return {
        "slot": link.get("slot"),
        "slug": slug,
        "asin": link.get("asin"),
        "product_name": link.get("product_name"),
        "first_live_at": lifecycle_map.get(slug, {}).get("first_live_at"),
        "clicks_30d": performance.get("clicks_30d", 0),
        "affiliate_clicks_30d": performance.get("affiliate_clicks_30d", 0),
        "impressions_30d": performance.get("impressions_30d", 0),
        "snapshot_status": snapshot_status(snapshot),
    }


def decide_next_action(live_items: list[dict[str, Any]]) -> tuple[bool, str]:
    """Decide the next money action."""
    metrics_need_update = any(
        item["snapshot_status"] != "fresh"
        for item in live_items
    )

    if metrics_need_update and live_items:
        return True, "update_amazon_metrics_snapshot"

    if not live_items:
        return False, "add_first_approved_amazon_link"

    return False, "monitor_live_products"


def build_money_status() -> dict[str, Any]:
    """Build money monitor status."""
    registry = load_json(REGISTRY, {"links": []})
    lifecycle = load_json(LIFECYCLE, {"items": []})
    performance = load_json(PERFORMANCE, {"items": []})
    snapshots = load_json(SNAPSHOTS, {"snapshots": []})

    lifecycle_map = map_by_slug(lifecycle)
    performance_map = map_by_slug(performance)
    snapshot_map = snapshot_by_slug(snapshots)

    live_items = [
        build_live_item(link, lifecycle_map, performance_map, snapshot_map)
        for link in live_links(registry)
    ]

    metrics_need_update, next_action = decide_next_action(live_items)

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "money_monitor_ready",
        "live_amazon_links": len(live_items),
        "live_items": live_items,
        "metrics_need_update": metrics_need_update,
        "next_money_action": next_action,
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }

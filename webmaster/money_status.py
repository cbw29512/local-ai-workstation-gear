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

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "amazon_links" / "approved_amazon_links.json"
LIFECYCLE = ROOT / "data" / "item_lifecycle.json"
PERFORMANCE = ROOT / "data" / "performance" / "item_performance.json"
SNAPSHOTS = ROOT / "data" / "performance" / "amazon_click_snapshots.json"
LOG_FILE = ROOT / "logs" / "money_status.log"


def setup_logging() -> None:
    """Create money monitor logging."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    """Load JSON or return a fallback if missing."""
    try:
        if not path.is_file():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        return fallback


def live_links(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return Chris-approved live Amazon links."""
    return [
        link for link in registry.get("links", [])
        if link.get("approved_by_chris") is True
        and link.get("live_enabled") is True
    ]


def lifecycle_by_slug(lifecycle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map lifecycle items by slug."""
    return {
        item["slug"]: item
        for item in lifecycle.get("items", [])
        if item.get("slug")
    }


def performance_by_slug(performance: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map performance items by slug."""
    return {
        item["slug"]: item
        for item in performance.get("items", [])
        if item.get("slug")
    }


def snapshot_by_slug(snapshot_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map manual metric snapshots by slug."""
    return {
        item["slug"]: item
        for item in snapshot_data.get("snapshots", [])
        if item.get("slug")
    }


def snapshot_status(snapshot: dict[str, Any] | None) -> str:
    """Classify manual Amazon metric snapshot freshness."""
    if not snapshot:
        return "missing"

    captured = snapshot.get("captured_at")

    if not captured:
        return "missing_capture_time"

    try:
        captured_at = datetime.fromisoformat(captured)
    except Exception:
        return "invalid_capture_time"

    age_days = (datetime.now(timezone.utc) - captured_at).days

    if age_days > 7:
        return "stale"

    return "fresh"


def build_money_status() -> dict[str, Any]:
    """Build money monitor status."""
    registry = load_json(REGISTRY, {"links": []})
    lifecycle = load_json(LIFECYCLE, {"items": []})
    performance = load_json(PERFORMANCE, {"items": []})
    snapshots = load_json(SNAPSHOTS, {"snapshots": []})

    links = live_links(registry)
    lifecycle_map = lifecycle_by_slug(lifecycle)
    performance_map = performance_by_slug(performance)
    snapshot_map = snapshot_by_slug(snapshots)

    live_items = []

    for link in links:
        slug = link["slug"]
        snapshot = snapshot_map.get(slug)
        status = snapshot_status(snapshot)

        live_items.append(
            {
                "slot": link.get("slot"),
                "slug": slug,
                "asin": link.get("asin"),
                "product_name": link.get("product_name"),
                "first_live_at": lifecycle_map.get(slug, {}).get("first_live_at"),
                "clicks_30d": performance_map.get(slug, {}).get("clicks_30d", 0),
                "affiliate_clicks_30d": performance_map.get(slug, {}).get("affiliate_clicks_30d", 0),
                "impressions_30d": performance_map.get(slug, {}).get("impressions_30d", 0),
                "snapshot_status": status,
            }
        )

    metrics_need_update = any(
        item["snapshot_status"] != "fresh"
        for item in live_items
    )

    if metrics_need_update and live_items:
        next_action = "update_amazon_metrics_snapshot"
    elif not live_items:
        next_action = "add_first_approved_amazon_link"
    else:
        next_action = "monitor_live_products"

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "money_monitor_ready",
        "live_amazon_links": len(links),
        "live_items": live_items,
        "metrics_need_update": metrics_need_update,
        "next_money_action": next_action,
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }

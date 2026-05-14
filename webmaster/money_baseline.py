"""
Build initial timestamped money baseline snapshots.

Safety:
- Does not invent traffic.
- Does not change affiliate links.
- Does not swap products.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.amazon_links_io import load_json, write_json
from webmaster.amazon_links_paths import LINK_REGISTRY as REGISTRY
from webmaster.performance_paths import ROOT


SNAPSHOTS = ROOT / "data" / "performance" / "amazon_click_snapshots.json"


def live_links(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return Chris-approved live Amazon links."""
    return [
        link
        for link in registry.get("links", [])
        if link.get("approved_by_chris") is True
        and link.get("live_enabled") is True
    ]


def existing_by_slug(snapshot_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Preserve existing manual metric rows by slug."""
    return {
        row["slug"]: row
        for row in snapshot_data.get("snapshots", [])
        if row.get("slug")
    }


def build_snapshot_row(link: dict[str, Any], old: dict[str, Any], now: str) -> dict[str, Any]:
    """Create or preserve one metric snapshot row."""
    return {
        "captured_at": old.get("captured_at") or now,
        "slot": link.get("slot"),
        "slug": link.get("slug"),
        "asin": link.get("asin"),
        "product_name": link.get("product_name"),
        "clicks_30d": int(old.get("clicks_30d", 0)),
        "affiliate_clicks_30d": int(old.get("affiliate_clicks_30d", 0)),
        "impressions_30d": int(old.get("impressions_30d", 0)),
        "ctr_30d": float(old.get("ctr_30d", 0.0)),
        "notes": old.get(
            "notes",
            "Initial baseline. Replace with Amazon Associates/Search Console data later.",
        ),
    }


def build_baseline_snapshot() -> dict[str, Any]:
    """Build baseline snapshot document."""
    registry = load_json(REGISTRY)
    snapshot_data = load_json(SNAPSHOTS) if SNAPSHOTS.is_file() else {
        "status": "manual_amazon_metrics_snapshot_ready",
        "source": "Amazon Associates manual report import",
        "snapshots": [],
    }

    now = datetime.now(timezone.utc).isoformat()
    old_rows = existing_by_slug(snapshot_data)
    links = live_links(registry)

    rows = [
        build_snapshot_row(link, old_rows.get(link["slug"], {}), now)
        for link in links
    ]

    snapshot_data["status"] = "manual_amazon_metrics_snapshot_ready"
    snapshot_data["source"] = "Amazon Associates manual report import"
    snapshot_data["updated_at"] = now
    snapshot_data["snapshots"] = rows
    snapshot_data["replacement_allowed"] = False
    snapshot_data["product_swap_allowed"] = False
    snapshot_data["affiliate_link_changes_allowed"] = False
    snapshot_data["git_commit_allowed"] = False
    snapshot_data["git_push_allowed"] = False
    snapshot_data["publish_allowed"] = False

    return snapshot_data


def write_baseline_snapshot() -> dict[str, Any]:
    """Build and write baseline snapshot."""
    snapshot = build_baseline_snapshot()
    write_json(SNAPSHOTS, snapshot)
    return snapshot

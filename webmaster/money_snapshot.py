"""
Money monitor snapshot helpers.

Classifies manual Amazon metrics snapshot freshness.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


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

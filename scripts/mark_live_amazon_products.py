"""
Mark Chris-approved live Amazon products in lifecycle/performance data.

State:
- Reads approved Amazon link registry.
- Updates first_live_at for live products.
- Updates performance metric source.

Safety:
- No product swaps.
- No affiliate link changes.
- No commits or pushes.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
LIFECYCLE = ROOT / "data/item_lifecycle.json"
PERFORMANCE = ROOT / "data/performance/item_performance.json"


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON safely."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to load {path}: {exc}") from exc


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON safely."""
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Failed to write {path}: {exc}") from exc


def live_slugs(registry: dict[str, Any]) -> set[str]:
    """Return slugs with Chris-approved live Amazon links."""
    return {
        link["slug"]
        for link in registry.get("links", [])
        if link.get("approved_by_chris") is True
        and link.get("live_enabled") is True
    }


def mark_lifecycle(lifecycle: dict[str, Any], slugs: set[str], now: str) -> int:
    """Mark lifecycle entries as live testing."""
    count = 0

    for item in lifecycle.get("items", []):
        if item.get("slug") not in slugs:
            continue

        if item.get("first_live_at") is None:
            item["first_live_at"] = now

        item["status"] = "live_testing"
        item["rotation_status"] = item.get("rotation_status") or "testing"
        item["last_reviewed_at"] = now
        item["replacement_allowed"] = False
        count += 1

    lifecycle["updated_at"] = now
    return count


def mark_performance(performance: dict[str, Any], slugs: set[str], now: str) -> int:
    """Mark performance records as awaiting Amazon report data."""
    count = 0

    for item in performance.get("items", []):
        if item.get("slug") not in slugs:
            continue

        item["metric_source"] = "amazon_associates_manual_import_pending"
        item["last_metric_snapshot_at"] = now
        item["replacement_allowed"] = False
        item["product_swap_allowed"] = False
        item["affiliate_link_changes_allowed"] = False
        count += 1

    performance["updated_at"] = now
    return count


def main() -> int:
    """Mark live Amazon products."""
    try:
        registry = load_json(REGISTRY)
        lifecycle = load_json(LIFECYCLE)
        performance = load_json(PERFORMANCE)
        now = datetime.now(timezone.utc).isoformat()

        slugs = live_slugs(registry)
        lifecycle_count = mark_lifecycle(lifecycle, slugs, now)
        performance_count = mark_performance(performance, slugs, now)

        write_json(LIFECYCLE, lifecycle)
        write_json(PERFORMANCE, performance)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"live_slugs: {len(slugs)}")
    print(f"lifecycle_marked: {lifecycle_count}")
    print(f"performance_marked: {performance_count}")
    print("next_required_gate: amazon_metrics_snapshot_import")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

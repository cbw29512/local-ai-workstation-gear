"""
Import manual Amazon/Search Console performance snapshots.

State:
- Reads data/performance/amazon_click_snapshots.json.
- Updates data/performance/item_performance.json.

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
SNAPSHOTS = ROOT / "data/performance/amazon_click_snapshots.json"
PERFORMANCE = ROOT / "data/performance/item_performance.json"


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON."""
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def snapshot_by_slug(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map latest snapshot rows by slug."""
    return {
        row["slug"]: row
        for row in data.get("snapshots", [])
        if row.get("slug")
    }


def main() -> int:
    """Import manual metrics into performance records."""
    try:
        snapshots = load_json(SNAPSHOTS)
        performance = load_json(PERFORMANCE)
        rows = snapshot_by_slug(snapshots)
        now = datetime.now(timezone.utc).isoformat()
        updated = 0

        for item in performance.get("items", []):
            row = rows.get(item.get("slug"))
            if not row:
                continue

            item["clicks_30d"] = int(row.get("clicks_30d", 0))
            item["affiliate_clicks_30d"] = int(row.get("affiliate_clicks_30d", 0))
            item["impressions_30d"] = int(row.get("impressions_30d", 0))
            item["ctr_30d"] = float(row.get("ctr_30d", 0.0))
            item["last_metric_snapshot_at"] = row.get("captured_at") or now
            item["metric_source"] = snapshots.get("source", "manual_import")
            updated += 1

        performance["updated_at"] = now
        write_json(PERFORMANCE, performance)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"metrics_updated: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

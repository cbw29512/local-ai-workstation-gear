"""
Create initial timestamped baseline metrics for live Amazon products.

State schema:
{
  "captured_at": "UTC timestamp",
  "slot": int,
  "slug": str,
  "asin": str,
  "product_name": str,
  "clicks_30d": 0,
  "affiliate_clicks_30d": 0,
  "impressions_30d": 0,
  "ctr_30d": 0.0
}

Safety:
- Does not invent traffic.
- Does not change affiliate links.
- Does not swap products.
- Does not commit or push.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "amazon_links" / "approved_amazon_links.json"
SNAPSHOTS = ROOT / "data" / "performance" / "amazon_click_snapshots.json"
LOG_FILE = ROOT / "logs" / "set_initial_money_baseline.log"


def setup_logging() -> None:
    """Create traceable logs for baseline creation."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    """Load JSON with fallback."""
    try:
        if not path.is_file():
            return fallback

        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        return fallback


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON safely."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write %s: %s", path, exc)
        raise


def live_links(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return Chris-approved live Amazon links."""
    return [
        link for link in registry.get("links", [])
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


def main() -> int:
    """Create baseline snapshot for live links."""
    setup_logging()

    try:
        registry = load_json(REGISTRY, {"links": []})
        snapshot_data = load_json(
            SNAPSHOTS,
            {
                "status": "manual_amazon_metrics_snapshot_ready",
                "source": "Amazon Associates manual report import",
                "snapshots": [],
            },
        )

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

        write_json(SNAPSHOTS, snapshot_data)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"live_snapshot_rows: {len(rows)}")
    print("next_required_gate: import_manual_amazon_metrics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

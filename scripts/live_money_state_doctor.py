"""
Validate live money item tracking state.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
LIFECYCLE = ROOT / "data/item_lifecycle.json"
PERFORMANCE = ROOT / "data/performance/item_performance.json"


def load_json(path: Path) -> dict:
    """Load JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    """Validate live money tracking state."""
    problems: list[str] = []

    registry = load_json(REGISTRY)
    lifecycle = load_json(LIFECYCLE)
    performance = load_json(PERFORMANCE)

    live_slugs = {
        link["slug"]
        for link in registry.get("links", [])
        if link.get("approved_by_chris") is True
        and link.get("live_enabled") is True
    }

    lifecycle_map = {item["slug"]: item for item in lifecycle.get("items", [])}
    performance_map = {item["slug"]: item for item in performance.get("items", [])}

    if not live_slugs:
        problems.append("no live Amazon links found")

    for slug in live_slugs:
        if lifecycle_map.get(slug, {}).get("first_live_at") is None:
            problems.append(f"{slug}: first_live_at missing")

        source = performance_map.get(slug, {}).get("metric_source", "")
        if "amazon" not in source:
            problems.append(f"{slug}: performance metric source not Amazon-aware")

    print("RESULT:")

    if problems:
        print("LIVE MONEY STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("LIVE MONEY STATE: PASS")
    print(f"live_amazon_links: {len(live_slugs)}")
    print("next_required_gate: monitor_affiliate_clicks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

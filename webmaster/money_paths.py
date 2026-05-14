"""
Money monitor path constants.

State first:
- Paths only.
- No affiliate link changes.
- No swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "amazon_links" / "approved_amazon_links.json"
LIFECYCLE = ROOT / "data" / "item_lifecycle.json"
PERFORMANCE = ROOT / "data" / "performance" / "item_performance.json"
SNAPSHOTS = ROOT / "data" / "performance" / "amazon_click_snapshots.json"
LOG_FILE = ROOT / "logs" / "money_status.log"

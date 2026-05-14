"""
Lifecycle path constants.

State first:
- Paths only.
- No affiliate links, product swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ITEMS_JSON = ROOT / "data" / "items.json"
POLICY_JSON = ROOT / "data" / "rotation_policy.json"
LIFECYCLE_JSON = ROOT / "data" / "item_lifecycle.json"
LOG_FILE = ROOT / "logs" / "apply_lifecycle_timestamps.log"

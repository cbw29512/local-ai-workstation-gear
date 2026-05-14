"""
Performance path constants.

State first:
- Paths only.
- No affiliate links, product swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ITEMS_JSON = ROOT / "data" / "items.json"
PERFORMANCE_POLICY_JSON = ROOT / "data" / "performance" / "performance_policy.json"
ITEM_PERFORMANCE_JSON = ROOT / "data" / "performance" / "item_performance.json"
ROTATION_REPORT_JSON = ROOT / "reports" / "rotation" / "rotation_decision_report.json"
ROTATION_REPORT_MD = ROOT / "reports" / "rotation" / "rotation_decision_report.md"

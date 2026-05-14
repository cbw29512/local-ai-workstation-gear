"""
Vertical result path constants.

State:
- Paths only.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "data/site_portfolio/cloud_vertical_handoff.json"
FALLBACK_RESULT = ROOT / "data/site_portfolio/cloud_vertical_results/home-organization.json"
LOG_FILE = ROOT / "logs/cloud_vertical_result_doctor.log"

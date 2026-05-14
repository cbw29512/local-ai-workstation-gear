"""
Vertical proposal path constants.

State:
- Paths only.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/site_portfolio/vertical_diversification_policy.json"
PROPOSALS_JSON = ROOT / "data/site_portfolio/non_tech_vertical_proposals.json"
PROPOSALS_MD = ROOT / "data/site_portfolio/non_tech_vertical_proposals.md"
LOG_FILE = ROOT / "logs/vertical_proposals.log"

"""
Vertical workflow audit path constants.

State:
- Paths only.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "data/site_portfolio/cloud_vertical_active_prompts/home-organization-active-prompt.md"
HANDOFF = ROOT / "data/site_portfolio/cloud_vertical_handoff.json"
STAGED = ROOT / "data/site_portfolio/cloud_vertical_results/staged-home-organization.json"
ACTIVE = ROOT / "data/site_portfolio/cloud_vertical_results/home-organization.json"
LOG_FILE = ROOT / "logs/vertical_workflow_audit.log"

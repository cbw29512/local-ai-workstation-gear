"""
Cloud vertical research packet path constants.

State:
- Paths only.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSALS = ROOT / "data/site_portfolio/non_tech_vertical_proposals.json"
PACKET_DIR = ROOT / "data/site_portfolio/cloud_vertical_packets"
QUEUE_JSON = ROOT / "data/site_portfolio/cloud_vertical_research_queue.json"
QUEUE_MD = ROOT / "data/site_portfolio/cloud_vertical_research_queue.md"
LOG_FILE = ROOT / "logs/vertical_research_packets.log"

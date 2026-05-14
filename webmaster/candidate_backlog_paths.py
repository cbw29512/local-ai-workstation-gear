"""
Candidate backlog path constants.

State first:
- Paths only.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ITEMS_JSON = ROOT / "data" / "items.json"
LINK_REGISTRY = ROOT / "data" / "amazon_links" / "approved_amazon_links.json"
AMAZON_RESULTS = ROOT / "data" / "product_review" / "research_results" / "batch_01_amazon_only_results.json"
POLICY = ROOT / "data" / "product_candidates" / "candidate_backlog_policy.json"
BACKLOG_JSON = ROOT / "data" / "product_candidates" / "candidate_backlog.json"
CLOUD_PACKET_DIR = ROOT / "data" / "product_candidates" / "cloud_packets"

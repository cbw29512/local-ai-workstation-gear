"""
Candidate proposal path constants.

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
POLICY = ROOT / "data" / "product_candidates" / "local_candidate_policy.json"
PROPOSAL_JSON = ROOT / "data" / "product_candidates" / "local_candidate_proposal.json"
CLOUD_PACKET_MD = ROOT / "reports" / "product_candidates" / "cloud_clarification_packet.md"
LOG_FILE = ROOT / "logs" / "candidate_proposal.log"

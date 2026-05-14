"""
Approved candidate queue path constants.

State:
- Paths only.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "data/product_candidates/cloud_candidate_clarification.json"
BACKLOG = ROOT / "data/product_candidates/backlog_cloud_clarifications.json"
QUEUE_JSON = ROOT / "data/product_candidates/approved_candidate_queue.json"
QUEUE_MD = ROOT / "data/product_candidates/approved_candidate_queue.md"
LOG_FILE = ROOT / "logs/approved_candidate_queue.log"

"""
Generated affiliate link intake path constants.

State:
- Paths only.
- No affiliate links are created here.
- No product swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "data/amazon_links/generated_affiliate_links_from_queue.json"
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
BACKUP = ROOT / "data/amazon_links/approved_amazon_links.backup.json"
LOG_FILE = ROOT / "logs/intake_generated_affiliate_links.log"

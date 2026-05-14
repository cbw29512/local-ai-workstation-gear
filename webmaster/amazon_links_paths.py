"""
Amazon link path constants.

State first:
- Paths only.
- No affiliate links are created here.
- No commits, pushes, publishing, or external actions.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMAZON_RESULTS = ROOT / "data/product_review/research_results/batch_01_amazon_only_results.json"
LINK_REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
SITES_DIR = ROOT / "sites"
DOCS_DIR = ROOT / "docs"
OUT_DIR = ROOT / "docs" / "out"

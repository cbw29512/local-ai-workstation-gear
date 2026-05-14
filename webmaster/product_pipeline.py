"""
Product pipeline status for the local AI webmaster.

State schema:
{
  "item_count": int,
  "product_packet_count": int,
  "batch_01_results_exists": bool,
  "affiliate_link_changes_allowed": false,
  "git_commit_allowed": false,
  "git_push_allowed": false
}

Safety:
- Read-only.
- No affiliate links.
- No product swaps.
- No commits or pushes.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from webmaster.paths import ROOT


ITEMS_JSON = ROOT / "data" / "items.json"
PRODUCT_RESEARCH_DIR = ROOT / "data" / "product_research"
BATCH_01_RESULTS = (
    ROOT
    / "data"
    / "product_review"
    / "research_results"
    / "batch_01_cloud_review_results.json"
)


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with useful failure logging."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load JSON from %s: %s", path, exc)
        raise


def count_items() -> int:
    """Count item slots from the source-of-truth inventory."""
    inventory = load_json(ITEMS_JSON)
    items = inventory.get("items", [])
    return len(items) if isinstance(items, list) else 0


def count_product_packets() -> int:
    """Count generated product research packets."""
    if not PRODUCT_RESEARCH_DIR.is_dir():
        return 0

    return len(list(PRODUCT_RESEARCH_DIR.glob("*.json")))


def batch_01_status() -> dict[str, Any]:
    """Inspect Batch 01 result state if present."""
    if not BATCH_01_RESULTS.is_file():
        return {
            "batch_01_results_exists": False,
            "batch_01_reviewed_slots": 0,
            "batch_01_ready_for_chris_review": False,
        }

    data = load_json(BATCH_01_RESULTS)
    slots = data.get("slots", [])

    return {
        "batch_01_results_exists": True,
        "batch_01_reviewed_slots": len(slots) if isinstance(slots, list) else 0,
        "batch_01_ready_for_chris_review": data.get("ready_for_chris_review") is True,
    }


def build_product_pipeline_status() -> dict[str, Any]:
    """Build the read-only product pipeline status."""
    status = {
        "item_count": count_items(),
        "product_packet_count": count_product_packets(),
        **batch_01_status(),
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
    }

    return status

"""
Monthly swap proposal logic.

The local AI may propose swaps.
It may not execute swaps without approval.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_swap_candidates(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    """Create review-only swap candidates from item statuses."""
    candidates: list[dict[str, Any]] = []

    for item in inventory.get("items", []):
        status = str(item.get("status", ""))

        if status in {"needs_product_review", "stale", "underperforming"}:
            candidates.append(
                {
                    "slot": item.get("slot"),
                    "slug": item.get("slug"),
                    "title": item.get("title"),
                    "current_status": status,
                    "proposal": "review_for_possible_replacement_or_upgrade",
                    "approval_required": True,
                }
            )

    return candidates


def build_monthly_packet(inventory: dict[str, Any]) -> dict[str, Any]:
    """Build a monthly product swap proposal packet."""
    now = datetime.now(timezone.utc)

    return {
        "created_at": now.isoformat(),
        "month": now.strftime("%Y-%m"),
        "status": "monthly_swap_proposal_created",
        "swap_candidates": build_swap_candidates(inventory),
        "product_swap_allowed": False,
        "affiliate_link_changes_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "cloud_review_required": True,
        "human_approval_required": True,
        "next_required_gate": "cloud_ai_review_packet",
    }

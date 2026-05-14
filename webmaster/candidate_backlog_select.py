"""
Candidate backlog selection and item building.

Safety:
- Builds queued candidate rows only.
- No affiliate links.
- No product swaps.
- No publishing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.candidate_backlog_paths import CLOUD_PACKET_DIR
from webmaster.candidate_backlog_utils import valid_candidate


def build_backlog_item(
    slug: str,
    inventory: dict[str, dict[str, Any]],
    research: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build one queued backlog item."""
    now = datetime.now(timezone.utc).isoformat()
    item = inventory.get(slug, {})
    slot = research[slug]
    candidates = [
        candidate
        for candidate in slot.get("recommended_candidates", [])
        if valid_candidate(candidate)
    ]

    return {
        "created_at": now,
        "status": "queued_for_cloud_clarification",
        "slot": item.get("slot", slot.get("slot")),
        "slug": slug,
        "title": item.get("title", slug),
        "category": item.get("category", "unknown"),
        "recommended_candidates": candidates,
        "local_ai_recommendation": candidates[0],
        "cloud_packet": str(CLOUD_PACKET_DIR / f"{slug}.md"),
        "cloud_clarification_required": True,
        "human_approval_required": True,
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": "cloud_ai_candidate_clarification",
    }


def choose_backlog_slugs(
    priority: list[str],
    research: dict[str, dict[str, Any]],
    occupied: set[str],
    max_items: int,
) -> list[str]:
    """Choose backlog slugs from priority order."""
    chosen: list[str] = []

    for slug in priority:
        if slug in occupied:
            continue

        slot = research.get(slug)
        if not slot:
            continue

        if any(valid_candidate(candidate) for candidate in slot.get("recommended_candidates", [])):
            chosen.append(slug)

        if len(chosen) >= max_items:
            break

    return chosen

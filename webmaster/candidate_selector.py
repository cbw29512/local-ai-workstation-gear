"""
Select next local Amazon product candidate.

Local AI chooses from existing Amazon-only research.
Cloud AI must clarify before Chris approval.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.candidate_io import load_json
from webmaster.candidate_paths import AMAZON_RESULTS, ITEMS_JSON, LINK_REGISTRY, POLICY


def live_slugs(registry: dict[str, Any]) -> set[str]:
    """Return slugs already live-enabled."""
    return {
        link["slug"]
        for link in registry.get("links", [])
        if link.get("approved_by_chris") is True
        and link.get("live_enabled") is True
    }


def inventory_by_slug(items_json: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map item inventory by slug."""
    return {
        item["slug"]: item
        for item in items_json.get("items", [])
        if item.get("slug")
    }


def result_slots_by_slug(results: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map Amazon-only research slots by slug."""
    return {
        slot["slug"]: slot
        for slot in results.get("slots", [])
        if slot.get("slug")
    }


def valid_candidate(candidate: dict[str, Any]) -> bool:
    """Require Amazon URL and ASIN for proposal candidates."""
    url = str(candidate.get("amazon_url", ""))
    asin = str(candidate.get("asin", ""))
    return bool(asin) and ("amazon.com" in url or "amzn.to" in url)


def choose_slug(
    priority_slugs: list[str],
    research_by_slug: dict[str, dict[str, Any]],
    already_live: set[str],
) -> str | None:
    """Choose next slug from priority list first."""
    for slug in priority_slugs:
        if slug in already_live:
            continue

        slot = research_by_slug.get(slug)
        if not slot:
            continue

        candidates = slot.get("recommended_candidates", [])
        if any(valid_candidate(candidate) for candidate in candidates):
            return slug

    return None


def build_proposal() -> dict[str, Any]:
    """Build local candidate proposal."""
    items = load_json(ITEMS_JSON)
    registry = load_json(LINK_REGISTRY)
    results = load_json(AMAZON_RESULTS)
    policy = load_json(POLICY)

    already_live = live_slugs(registry)
    inventory = inventory_by_slug(items)
    research = result_slots_by_slug(results)
    priority = policy.get("priority_slugs", [])

    slug = choose_slug(priority, research, already_live)

    if not slug:
        return {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "no_candidate_available",
            "reason": "No non-live Amazon/ASIN candidate found in current research pool.",
            "next_required_gate": "cloud_ai_amazon_product_research",
        }

    slot = research[slug]
    candidates = [
        candidate
        for candidate in slot.get("recommended_candidates", [])
        if valid_candidate(candidate)
    ]

    inventory_item = inventory.get(slug, {})

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "local_candidate_proposed",
        "source": "local_ai_existing_amazon_research_pool",
        "slot": inventory_item.get("slot", slot.get("slot")),
        "slug": slug,
        "title": inventory_item.get("title", slug),
        "category": inventory_item.get("category", "unknown"),
        "recommended_candidates": candidates,
        "local_ai_recommendation": candidates[0] if candidates else {},
        "cloud_clarification_required": True,
        "human_approval_required": True,
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": "cloud_ai_candidate_clarification",
    }

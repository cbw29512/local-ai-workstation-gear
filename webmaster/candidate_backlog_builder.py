"""
Build a queued candidate backlog.

This lets the local AI keep preparing future Amazon candidates
while the current candidate waits for cloud/Chris approval.

Safety:
- Backlog only.
- No affiliate links.
- No product swaps.
- No publishing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.candidate_backlog_paths import (
    AMAZON_RESULTS,
    BACKLOG_JSON,
    CLOUD_PACKET_DIR,
    ITEMS_JSON,
    LINK_REGISTRY,
    POLICY,
)
from webmaster.candidate_cloud_packet import render_cloud_packet
from webmaster.candidate_gate_status import resolve_candidate_gate
from webmaster.candidate_io import load_json, write_json, write_text


def live_slugs(registry: dict[str, Any]) -> set[str]:
    """Return slugs already live-enabled."""
    return {
        link["slug"]
        for link in registry.get("links", [])
        if link.get("approved_by_chris") is True and link.get("live_enabled") is True
    }


def map_by_slug(data: dict[str, Any], key: str = "items") -> dict[str, dict[str, Any]]:
    """Map item-like records by slug."""
    return {item["slug"]: item for item in data.get(key, []) if item.get("slug")}


def research_by_slug(results: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map Amazon research slots by slug."""
    return {slot["slug"]: slot for slot in results.get("slots", []) if slot.get("slug")}


def valid_candidate(candidate: dict[str, Any]) -> bool:
    """Require Amazon URL and ASIN."""
    url = str(candidate.get("amazon_url", ""))
    asin = str(candidate.get("asin", ""))
    return bool(asin) and ("amazon.com" in url or "amzn.to" in url)


def existing_backlog_slugs() -> set[str]:
    """Return slugs already queued in backlog."""
    if not BACKLOG_JSON.is_file():
        return set()

    backlog = load_json(BACKLOG_JSON)
    return {
        item["slug"]
        for item in backlog.get("items", [])
        if item.get("status") == "queued_for_cloud_clarification"
    }


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


def build_backlog() -> dict[str, Any]:
    """Build candidate backlog document and durable cloud packets."""
    policy = load_json(POLICY)
    registry = load_json(LINK_REGISTRY)
    inventory = map_by_slug(load_json(ITEMS_JSON))
    research = research_by_slug(load_json(AMAZON_RESULTS))
    gate = resolve_candidate_gate()

    occupied = live_slugs(registry) | existing_backlog_slugs()
    if gate.get("slug"):
        occupied.add(gate["slug"])

    max_items = int(policy.get("max_backlog_items", 3))
    slugs = choose_backlog_slugs(policy.get("priority_slugs", []), research, occupied, max_items)

    items = [build_backlog_item(slug, inventory, research) for slug in slugs]

    CLOUD_PACKET_DIR.mkdir(parents=True, exist_ok=True)
    for item in items:
        write_text(CLOUD_PACKET_DIR / f"{item['slug']}.md", render_cloud_packet(item))

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate_backlog_created",
        "item_count": len(items),
        "items": items,
        "current_gate": gate.get("current_gate"),
        "current_gate_slug": gate.get("slug"),
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": "cloud_ai_backlog_clarification",
    }


def write_backlog() -> dict[str, Any]:
    """Build and write candidate backlog."""
    backlog = build_backlog()
    write_json(BACKLOG_JSON, backlog)
    return backlog

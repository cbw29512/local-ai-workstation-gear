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
from webmaster.candidate_backlog_select import build_backlog_item, choose_backlog_slugs
from webmaster.candidate_backlog_utils import (
    existing_backlog_slugs,
    live_slugs,
    map_by_slug,
    research_by_slug,
)
from webmaster.candidate_cloud_packet import render_cloud_packet
from webmaster.candidate_gate_status import resolve_candidate_gate
from webmaster.candidate_io import load_json, write_json, write_text


def occupied_slugs(registry: dict[str, Any], gate: dict[str, Any]) -> set[str]:
    """Return live, pending, and already queued slugs."""
    occupied = live_slugs(registry) | existing_backlog_slugs()

    if gate.get("slug"):
        occupied.add(gate["slug"])

    return occupied


def build_backlog() -> dict[str, Any]:
    """Build candidate backlog document and durable cloud packets."""
    policy = load_json(POLICY)
    registry = load_json(LINK_REGISTRY)
    inventory = map_by_slug(load_json(ITEMS_JSON))
    research = research_by_slug(load_json(AMAZON_RESULTS))
    gate = resolve_candidate_gate()

    max_items = int(policy.get("max_backlog_items", 3))
    slugs = choose_backlog_slugs(
        policy.get("priority_slugs", []),
        research,
        occupied_slugs(registry, gate),
        max_items,
    )

    items = [
        build_backlog_item(slug, inventory, research)
        for slug in slugs
    ]

    CLOUD_PACKET_DIR.mkdir(parents=True, exist_ok=True)

    for item in items:
        packet = render_cloud_packet(item)
        write_text(CLOUD_PACKET_DIR / f"{item['slug']}.md", packet)

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

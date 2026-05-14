"""
Generate cloud research packets for non-tech Amazon affiliate verticals.

State:
- Reads non-tech vertical proposals.
- Writes one durable cloud research packet per vertical.
- Writes a queue file for cloud AI review.

Safety:
- Research packets only.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.vertical_research_io import load_json, setup_logging, write_json, write_text
from webmaster.vertical_research_paths import PACKET_DIR, PROPOSALS, QUEUE_JSON, QUEUE_MD
from webmaster.vertical_research_render import locked_flags, render_packet, render_queue_markdown


def packet_path(vertical_slug: str):
    """Return packet path for one vertical."""
    return PACKET_DIR / f"{vertical_slug}.md"


def build_vertical_row(proposal: dict[str, Any]) -> dict[str, Any]:
    """Build one queue row from a vertical proposal."""
    path = packet_path(proposal["vertical_slug"])
    write_text(path, render_packet(proposal))

    return {
        "vertical_slug": proposal["vertical_slug"],
        "site_angle": proposal["site_angle"],
        "packet_path": str(path),
        "required_output": "24 Amazon-only item candidates",
        "cloud_research_required": True,
        "human_approval_required": True,
        **locked_flags(),
    }


def build_queue() -> dict[str, Any]:
    """Build vertical research queue and packet files."""
    proposals = load_json(PROPOSALS)
    PACKET_DIR.mkdir(parents=True, exist_ok=True)

    verticals = [
        build_vertical_row(proposal)
        for proposal in proposals.get("proposals", [])
    ]

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "cloud_vertical_research_queue_ready",
        "vertical_count": len(verticals),
        "verticals": verticals,
        "next_required_gate": "cloud_ai_vertical_product_research",
        **locked_flags(),
    }


def write_research_queue() -> dict[str, Any]:
    """Build and write cloud vertical research queue."""
    setup_logging()
    queue = build_queue()
    write_json(QUEUE_JSON, queue)
    write_text(QUEUE_MD, render_queue_markdown(queue))
    return queue

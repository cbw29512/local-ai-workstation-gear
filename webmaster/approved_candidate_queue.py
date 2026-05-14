"""
Build approved candidate queue.

State:
- Reads primary cloud clarification.
- Reads backlog cloud clarifications if present.
- Writes one durable queue of products waiting for Chris-approved affiliate URLs.

Safety:
- No affiliate links are created.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.approved_queue_collect import collect_backlog, collect_primary, dedupe, locked_flags
from webmaster.approved_queue_io import load_optional, setup_logging, write_json, write_text
from webmaster.approved_queue_paths import BACKLOG, PRIMARY, QUEUE_JSON, QUEUE_MD
from webmaster.approved_queue_render import render_markdown


def build_queue() -> dict[str, Any]:
    """Build approved candidate queue."""
    setup_logging()
    primary = load_optional(PRIMARY)
    backlog = load_optional(BACKLOG)

    backlog_approved, held = collect_backlog(backlog)
    approved = dedupe(collect_primary(primary) + backlog_approved)

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "approved_candidate_queue_ready",
        "approved_count": len(approved),
        "held_count": len(held),
        "approved_items": approved,
        "held_items": held,
        "next_required_gate": "chris_affiliate_url_for_approved_candidates",
        **locked_flags(),
    }


def write_queue() -> dict[str, Any]:
    """Build and write approved candidate queue."""
    queue = build_queue()
    write_json(QUEUE_JSON, queue)
    write_text(QUEUE_MD, render_markdown(queue))
    return queue

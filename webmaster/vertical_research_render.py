"""
Render cloud vertical research packets.

The generated packet intentionally avoids Markdown code fences inside
Python strings to reduce paste/heredoc breakage risk.
"""

from __future__ import annotations

from typing import Any


def locked_flags() -> dict[str, bool]:
    """Return safety locks."""
    return {
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }


def render_packet(proposal: dict[str, Any]) -> str:
    """Render one cloud AI research packet."""
    angles = "\n".join(
        f"- {angle}"
        for angle in proposal.get("example_item_angles", [])
    )

    return f"""# Cloud Vertical Product Research Packet

Vertical: {proposal["vertical_slug"]}

Site angle:
{proposal["site_angle"]}

## Example Item Angles

{angles}

## Task For Large/Cloud AI

Find 24 Amazon-only product candidates for this vertical.

## Hard Rules

- Amazon-only.
- Each candidate must include an Amazon URL.
- ASIN is required when available.
- Do not create affiliate links.
- Do not invent prices.
- Do not invent ratings.
- Do not invent reviews.
- Do not invent discounts.
- Do not recommend blocked categories.
- Avoid medical, legal, financial, or safety claims.
- Favor useful, item-first pages with clear descriptions.
- Chris approval is required before any product goes live.

## Required Output Shape

Return JSON with:
- vertical_slug
- status: cloud_vertical_research_completed
- recommended_site_name
- definition_of_done
- items: 24 rows
- global_risk_notes
- ready_for_chris_review
- affiliate_links_created: false
- publish_recommended: false

Each item row must include:
- slot
- page_slug
- page_title
- product_name
- brand
- asin
- amazon_url
- why_it_fits
- item_angle
- important_specs_to_verify
- risk_notes
- confidence
"""


def render_queue_markdown(queue: dict[str, Any]) -> str:
    """Render queue as Markdown."""
    rows = [
        f"- `{item['vertical_slug']}` — {item['site_angle']}"
        for item in queue["verticals"]
    ]

    return f"""# Cloud Vertical Research Queue

Status: `{queue["status"]}`

Vertical count: `{queue["vertical_count"]}`

Next required gate: `{queue["next_required_gate"]}`

## Verticals

{chr(10).join(rows)}

## Safety Locks

- Affiliate link changes allowed: `{queue["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{queue["product_swap_allowed"]}`
- Git commit allowed: `{queue["git_commit_allowed"]}`
- Git push allowed: `{queue["git_push_allowed"]}`
- Publish allowed: `{queue["publish_allowed"]}`
"""

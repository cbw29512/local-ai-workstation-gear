"""
Render approved candidate queue as Markdown.
"""

from __future__ import annotations

from typing import Any


def render_markdown(queue: dict[str, Any]) -> str:
    """Render queue as Markdown."""
    approved_rows = [
        f"- Slot {item['slot']} `{item['slug']}`: "
        f"{item['product_name']} / ASIN `{item['asin']}`"
        for item in queue["approved_items"]
    ]

    held_rows = [
        f"- Slot {item['slot']} `{item['slug']}`: "
        f"{item['product_name']} / decision `{item['final_decision']}`"
        for item in queue["held_items"]
    ]

    return f"""# Approved Candidate Queue

Status: `{queue["status"]}`

Approved waiting for Chris affiliate URL: `{queue["approved_count"]}`

Held candidates: `{queue["held_count"]}`

## Approved Items

{chr(10).join(approved_rows) if approved_rows else "- None"}

## Held Items

{chr(10).join(held_rows) if held_rows else "- None"}

## Safety Locks

- Affiliate link changes allowed: `{queue["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{queue["product_swap_allowed"]}`
- Git commit allowed: `{queue["git_commit_allowed"]}`
- Git push allowed: `{queue["git_push_allowed"]}`
- Publish allowed: `{queue["publish_allowed"]}`
"""

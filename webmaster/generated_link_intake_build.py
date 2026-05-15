"""
Build generated affiliate link registry rows.

Safety:
- Converts staged generated links to registry rows.
- Keeps live_enabled false.
- No publishing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def key_for(row: dict[str, Any]) -> tuple[str, str]:
    """Return slug/ASIN key."""
    return str(row.get("slug", "")), str(row.get("asin", ""))


def build_existing_index(links: list[dict[str, Any]]) -> dict[tuple[str, str], int]:
    """Build lookup index for existing registry links."""
    return {key_for(row): position for position, row in enumerate(links)}


def registry_row(source: dict[str, Any]) -> dict[str, Any]:
    """Build registry row from generated link."""
    return {
        "slot": source.get("slot"),
        "slug": source.get("slug"),
        "title": source.get("title"),
        "product_name": source.get("product_name"),
        "brand": source.get("brand"),
        "asin": source.get("asin"),
        "source_amazon_url": source.get("source_amazon_url"),
        "affiliate_url": source.get("affiliate_url"),
        "approved_by_chris": True,
        "generated_from_universal_tag": True,
        "ready_for_page_injection": True,
        "live_enabled": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def upsert_links(registry: dict[str, Any], generated: dict[str, Any]) -> int:
    """Upsert generated links into registry."""
    links = registry.setdefault("links", [])

    if not isinstance(links, list):
        raise TypeError("registry links field must be a list")

    index = build_existing_index(links)
    changed = 0

    for source in generated.get("links", []):
        row = registry_row(source)
        key = key_for(row)

        if key in index:
            links[index[key]].update(row)
        else:
            links.append(row)

        changed += 1

    registry["updated_at"] = datetime.now(timezone.utc).isoformat()
    registry["next_required_gate"] = "inject_links_into_pages"
    registry["publish_allowed"] = False
    return changed

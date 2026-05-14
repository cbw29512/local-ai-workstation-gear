"""
Candidate backlog utility helpers.

Safety:
- Helper functions only.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from typing import Any

from webmaster.candidate_backlog_paths import BACKLOG_JSON
from webmaster.candidate_io import load_json


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

def existing_backlog_items() -> list[dict[str, Any]]:
    """Return existing queued backlog items so hourly runs do not erase them."""
    if not BACKLOG_JSON.is_file():
        return []

    backlog = load_json(BACKLOG_JSON)
    return [
        item
        for item in backlog.get("items", [])
        if item.get("status") == "queued_for_cloud_clarification"
    ]


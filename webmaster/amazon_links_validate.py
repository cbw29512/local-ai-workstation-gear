"""
Amazon link validation helpers.

Live links must be Amazon/amzn.to and explicitly approved by Chris.
"""

from __future__ import annotations

from typing import Any


PLACEHOLDER = "PASTE_CHRIS_APPROVED_AMAZON_AFFILIATE_URL_HERE"


def is_amazon_url(value: str) -> bool:
    """Return true for Amazon URLs or Amazon short links."""
    return "amazon.com" in value or "amzn.to" in value


def is_placeholder(value: str) -> bool:
    """Return true when an affiliate URL still needs Chris input."""
    return not value or PLACEHOLDER in value


def validate_registry(data: dict[str, Any]) -> list[str]:
    """Validate registry safety and live-link rules."""
    problems: list[str] = []
    links = data.get("links", [])

    if not isinstance(links, list) or not links:
        problems.append("links must be a non-empty list")

    for link in links:
        slug = link.get("slug", "unknown")
        amazon_url = str(link.get("amazon_url", ""))
        affiliate_url = str(link.get("approved_affiliate_url", ""))
        live_enabled = link.get("live_enabled") is True
        approved = link.get("approved_by_chris") is True

        if not is_amazon_url(amazon_url):
            problems.append(f"{slug}: amazon_url must be Amazon/amzn.to")

        if live_enabled:
            if not approved:
                problems.append(f"{slug}: live link requires approved_by_chris=true")

            if is_placeholder(affiliate_url):
                problems.append(f"{slug}: live link still has placeholder affiliate URL")

            if not is_amazon_url(affiliate_url):
                problems.append(f"{slug}: approved affiliate URL must be Amazon/amzn.to")

    for key in [
        "affiliate_link_changes_allowed",
        "product_swap_allowed",
        "git_commit_allowed",
        "git_push_allowed",
        "publish_allowed",
    ]:
        if data.get(key) is not False:
            problems.append(f"{key} must remain false")

    return problems


def approved_live_links(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only safe live links."""
    return [
        link
        for link in data.get("links", [])
        if link.get("approved_by_chris") is True
        and link.get("live_enabled") is True
        and not is_placeholder(str(link.get("approved_affiliate_url", "")))
    ]

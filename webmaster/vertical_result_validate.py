"""
Validate active cloud vertical research result.

Safety:
- Validation only.
- Cloud AI must not create affiliate links.
- Chris must approve before site creation or publishing.
"""

from __future__ import annotations

from typing import Any


def is_amazon_url(value: str) -> bool:
    """Return true for Amazon URLs or Amazon short links."""
    return "amazon.com" in value or "amzn.to" in value


def validate_item(item: dict[str, Any]) -> list[str]:
    """Validate one cloud-researched item."""
    problems: list[str] = []
    slug = item.get("page_slug", "unknown")
    required = ["slot", "page_slug", "page_title", "product_name", "brand", "amazon_url"]

    for key in required:
        if not item.get(key):
            problems.append(f"{slug}: missing {key}")

    if item.get("amazon_url") and not is_amazon_url(str(item["amazon_url"])):
        problems.append(f"{slug}: amazon_url must be Amazon/amzn.to")

    if item.get("affiliate_url") or item.get("approved_affiliate_url"):
        problems.append(f"{slug}: cloud AI must not create affiliate links")

    return problems


def validate_result(data: dict[str, Any], expected_slug: str) -> list[str]:
    """Validate full result file."""
    problems: list[str] = []
    items = data.get("items", [])

    if data.get("status") == "awaiting_cloud_vertical_research":
        return problems

    if data.get("status") != "cloud_vertical_research_completed":
        problems.append(f"bad status: {data.get('status')}")

    if data.get("vertical_slug") != expected_slug:
        problems.append(f"vertical_slug must be {expected_slug}")

    if len(items) != 24:
        problems.append(f"expected 24 items, got {len(items)}")

    for item in items:
        problems.extend(validate_item(item))

    for locked in [
        "affiliate_links_created",
        "publish_recommended",
        "affiliate_link_changes_allowed",
        "product_swap_allowed",
        "git_commit_allowed",
        "git_push_allowed",
        "publish_allowed",
    ]:
        if data.get(locked) is not False:
            problems.append(f"{locked} must be false")

    return problems

"""
Validate cloud vertical research result.

Read-only doctor.
No affiliate links, publishing, commits, pushes, or product swaps.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_FILE = ROOT / "data/site_portfolio/cloud_vertical_results/home_organization_result_template.json"


def is_amazon_url(value: str) -> bool:
    """Return true for Amazon URLs or Amazon short links."""
    return "amazon.com" in value or "amzn.to" in value


def validate_item(item: dict) -> list[str]:
    """Validate one returned product item."""
    problems: list[str] = []
    slug = item.get("page_slug", "unknown")

    required = [
        "slot",
        "page_slug",
        "page_title",
        "product_name",
        "brand",
        "amazon_url",
        "why_it_fits",
        "item_angle",
        "confidence",
    ]

    for key in required:
        if not item.get(key):
            problems.append(f"{slug}: missing {key}")

    if not is_amazon_url(str(item.get("amazon_url", ""))):
        problems.append(f"{slug}: amazon_url must be Amazon/amzn.to")

    if item.get("affiliate_url"):
        problems.append(f"{slug}: affiliate_url must not be created by cloud AI")

    return problems


def main() -> int:
    """Validate cloud vertical result."""
    problems: list[str] = []

    if not RESULT_FILE.is_file():
        problems.append("missing cloud vertical result file")
    else:
        data = json.loads(RESULT_FILE.read_text(encoding="utf-8"))
        items = data.get("items", [])

        if data.get("status") == "awaiting_cloud_vertical_research":
            print("RESULT:")
            print("CLOUD VERTICAL RESULT STATE: WAITING")
            print("Paste cloud research results before validation.")
            return 0

        if data.get("status") != "cloud_vertical_research_completed":
            problems.append(f"bad status: {data.get('status')}")

        if data.get("vertical_slug") != "home-organization":
            problems.append("vertical_slug must be home-organization")

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

    print("RESULT:")

    if problems:
        print("CLOUD VERTICAL RESULT STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CLOUD VERTICAL RESULT STATE: PASS")
    print("next_required_gate: chris_vertical_site_approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

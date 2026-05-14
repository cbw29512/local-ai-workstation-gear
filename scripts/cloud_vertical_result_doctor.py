"""
Validate cloud vertical research result.

State:
- Cloud AI may return product research.
- Cloud AI must not create affiliate links.
- Chris must approve before site creation or publishing.

Safety:
- Read-only doctor.
- No affiliate links.
- No product swaps.
- No commits or pushes.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_FILE = ROOT / "data/site_portfolio/cloud_vertical_results/home-organization.json"
LOG_FILE = ROOT / "logs/cloud_vertical_result_doctor.log"


def setup_logging() -> None:
    """Create doctor log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with useful failure context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


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


def validate_result(data: dict[str, Any]) -> list[str]:
    """Validate full result file."""
    problems: list[str] = []
    items = data.get("items", [])

    if data.get("status") == "awaiting_cloud_vertical_research":
        return problems

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

    return problems


def main() -> int:
    """Run cloud vertical result doctor."""
    setup_logging()

    try:
        data = load_json(RESULT_FILE)
    except Exception as exc:
        print("RESULT:")
        print("CLOUD VERTICAL RESULT STATE: NEEDS REVIEW")
        print(f"- {exc}")
        return 1

    if data.get("status") == "awaiting_cloud_vertical_research":
        print("RESULT:")
        print("CLOUD VERTICAL RESULT STATE: WAITING")
        print("Paste cloud research results before validation.")
        return 0

    problems = validate_result(data)

    print("RESULT:")

    if problems:
        print("CLOUD VERTICAL RESULT STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CLOUD VERTICAL RESULT STATE: PASS")
    print("vertical_slug: home-organization")
    print("item_count: 24")
    print("next_required_gate: chris_vertical_site_approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

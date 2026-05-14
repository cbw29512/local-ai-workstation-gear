"""
Validate cloud vertical research result.

Read-only doctor.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_FILE = ROOT / "data/site_portfolio/cloud_vertical_results/home_organization_result_template.json"


def is_amazon_url(value: str) -> bool:
    """Return true for Amazon URLs or Amazon short links."""
    return "amazon.com" in value or "amzn.to" in value


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

        if len(items) != 24:
            problems.append(f"expected 24 items, got {len(items)}")

        for item in items:
            slug = item.get("page_slug", "unknown")

            if not item.get("product_name"):
                problems.append(f"{slug}: missing product_name")

            if not item.get("amazon_url") or not is_amazon_url(str(item.get("amazon_url"))):
                problems.append(f"{slug}: missing Amazon URL")

            if item.get("affiliate_url"):
                problems.append(f"{slug}: affiliate_url must not be created by cloud AI")

        if data.get("affiliate_links_created") is not False:
            problems.append("affiliate_links_created must be false")

        if data.get("publish_recommended") is not False:
            problems.append("publish_recommended must be false")

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

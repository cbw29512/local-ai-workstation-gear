"""
Validate approved universal Amazon Associates tag.

State:
- Chris approved one Amazon tag/tracking ID.
- The system may generate product-specific URLs from approved ASINs.
- Generated URLs are still not published until live gates pass.

Safety:
- Read-only doctor.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAG_FILE = ROOT / "data/amazon_links/approved_universal_tag.json"


def main() -> int:
    """Validate universal Amazon tag policy."""
    problems: list[str] = []

    if not TAG_FILE.is_file():
        problems.append("missing approved universal tag file")
    else:
        data = json.loads(TAG_FILE.read_text(encoding="utf-8"))
        tag = str(data.get("amazon_tag", ""))

        if data.get("status") != "approved_universal_amazon_tag_active":
            problems.append("status must be approved_universal_amazon_tag_active")

        if not tag.endswith("-20"):
            problems.append("amazon_tag should look like a US Associates tracking ID ending in -20")

        if data.get("approved_by_chris") is not True:
            problems.append("approved_by_chris must be true")

        rules = data.get("rules", {})
        if rules.get("asin_required") is not True:
            problems.append("rules.asin_required must be true")

        if data.get("product_swap_allowed") is not False:
            problems.append("product_swap_allowed must be false")

        if data.get("publish_allowed") is not False:
            problems.append("publish_allowed must be false")

    print("RESULT:")

    if problems:
        print("UNIVERSAL AMAZON TAG STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("UNIVERSAL AMAZON TAG STATE: PASS")
    print("amazon_tag: maxyourheal06-20")
    print("next_required_gate: generate_approved_affiliate_urls_from_asins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

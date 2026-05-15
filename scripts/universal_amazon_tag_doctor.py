"""
Validate approved universal Amazon Associates tag.

State:
- Chris approved one Amazon tag/tracking ID.
- AI may generate product-specific Amazon affiliate button URLs from approved ASINs.
- Publishing still requires separate gates.

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
        rules = data.get("rules", {})

        if data.get("status") != "approved_universal_amazon_tag_active":
            problems.append("status must be approved_universal_amazon_tag_active")

        if data.get("amazon_tag") != "maxyourheal06-20":
            problems.append("amazon_tag must be maxyourheal06-20")

        if data.get("approved_by_chris") is not True:
            problems.append("approved_by_chris must be true")

        if data.get("affiliate_link_generation_allowed") is not True:
            problems.append("affiliate_link_generation_allowed must be true")

        if rules.get("ai_may_generate_affiliate_button_links") is not True:
            problems.append("AI affiliate button link generation must be allowed")

        if rules.get("manual_sitelink_creation_required") is not False:
            problems.append("manual_sitelink_creation_required must be false")

        if rules.get("asin_required") is not True:
            problems.append("ASIN must be required")

        if data.get("publish_allowed") is not False:
            problems.append("publish_allowed must be false")

        if data.get("product_swap_allowed") is not False:
            problems.append("product_swap_allowed must be false")

    print("RESULT:")

    if problems:
        print("UNIVERSAL AMAZON TAG STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("UNIVERSAL AMAZON TAG STATE: PASS")
    print("amazon_tag: maxyourheal06-20")
    print("ai_may_generate_affiliate_button_links: true")
    print("next_required_gate: generate_affiliate_urls_from_approved_asins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

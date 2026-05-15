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
import logging
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TAG_FILE = ROOT / "data/amazon_links/approved_universal_tag.json"
LOG_FILE = ROOT / "logs/universal_amazon_tag_doctor.log"


def setup_logging() -> None:
    """Create doctor log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with useful error context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def validate(data: dict[str, Any]) -> list[str]:
    """Validate universal tag policy."""
    problems: list[str] = []
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

    for locked in ["product_swap_allowed", "git_commit_allowed", "git_push_allowed", "publish_allowed"]:
        if data.get(locked) is not False:
            problems.append(f"{locked} must be false")

    return problems


def main() -> int:
    """Run universal tag doctor."""
    setup_logging()

    try:
        problems = validate(load_json(TAG_FILE))
    except Exception as exc:
        print("RESULT:")
        print("UNIVERSAL AMAZON TAG STATE: NEEDS REVIEW")
        print(f"- {exc}")
        return 1

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

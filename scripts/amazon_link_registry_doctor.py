"""
Validate Amazon affiliate link registry.

State schema:
{
  "status": str,
  "links": list,
  "approved_by_chris": bool,
  "live_enabled": bool
}

Safety:
- Read-only.
- No page edits.
- No commits or pushes.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"


def is_amazon_url(value: str) -> bool:
    """Allow Amazon product URLs or Amazon short links."""
    return "amazon.com" in value or "amzn.to" in value


def main() -> int:
    """Validate registry safety rules."""
    problems: list[str] = []

    if not REGISTRY.is_file():
        problems.append(f"missing registry: {REGISTRY}")
    else:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        links = data.get("links", [])

        if not links:
            problems.append("links list is empty")

        for link in links:
            slug = link.get("slug", "unknown")
            raw_url = link.get("amazon_url", "")
            affiliate_url = link.get("approved_affiliate_url", "")

            if not is_amazon_url(raw_url):
                problems.append(f"{slug}: amazon_url is not Amazon/amzn.to")

            if link.get("live_enabled") is True:
                if link.get("approved_by_chris") is not True:
                    problems.append(f"{slug}: live link must be approved by Chris")

                if "PASTE_" in affiliate_url or not is_amazon_url(affiliate_url):
                    problems.append(f"{slug}: live affiliate URL invalid")

        for key in ["affiliate_link_changes_allowed", "git_commit_allowed", "git_push_allowed"]:
            if data.get(key) is not False:
                problems.append(f"{key} must remain false")

    print("RESULT:")

    if problems:
        print("AMAZON LINK REGISTRY STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("AMAZON LINK REGISTRY STATE: PASS")
    print("Registry exists. Live links render only when approved_by_chris and live_enabled are true.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

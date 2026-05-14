"""
Validate cloud candidate clarification result.

Read-only doctor.
No affiliate links, product swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLARIFICATION = ROOT / "data/product_candidates/cloud_candidate_clarification.json"


def main() -> int:
    """Validate cloud clarification state."""
    problems: list[str] = []

    if not CLARIFICATION.is_file():
        problems.append("missing cloud candidate clarification")
    else:
        data = json.loads(CLARIFICATION.read_text(encoding="utf-8"))

        expected = {
            "status": "cloud_candidate_clarified",
            "final_decision": "approve",
            "best_candidate_asin": "B0CGW18S6Y",
            "affiliate_links_created": False,
            "approved_by_chris": False,
            "live_enabled": False,
            "affiliate_link_changes_allowed": False,
            "product_swap_allowed": False,
            "git_commit_allowed": False,
            "git_push_allowed": False,
            "publish_allowed": False
        }

        for key, value in expected.items():
            if data.get(key) != value:
                problems.append(f"{key} expected {value!r}, got {data.get(key)!r}")

        url = data.get("best_candidate_amazon_url", "")
        if "amazon.com" not in url and "amzn.to" not in url:
            problems.append("best candidate URL must be Amazon/amzn.to")

    print("RESULT:")

    if problems:
        print("CLOUD CANDIDATE CLARIFICATION STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CLOUD CANDIDATE CLARIFICATION STATE: PASS")
    print("next_required_gate: chris_affiliate_url_for_approved_candidate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

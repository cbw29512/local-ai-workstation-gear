"""
Validate Chris Batch 01 product review decision.

Read-only doctor.
No affiliate links, product swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "data/product_review/chris_decisions/batch_01_chris_review.json"


def main() -> int:
    """Validate Chris review decision file."""
    problems: list[str] = []

    if not DECISION.is_file():
        problems.append(f"missing decision file: {DECISION}")
    else:
        data = json.loads(DECISION.read_text(encoding="utf-8"))

        expected = {
            "batch": 1,
            "status": "chris_review_recorded",
            "affiliate_links_approved": False,
            "product_swap_allowed": False,
            "git_commit_allowed": False,
            "git_push_allowed": False,
            "publish_allowed": False,
            "next_required_gate": "draft_approved_product_pages",
        }

        for key, value in expected.items():
            if data.get(key) != value:
                problems.append(f"{key} expected {value!r}, got {data.get(key)!r}")

        if len(data.get("approved_for_draft_pages", [])) < 1:
            problems.append("at least one approved draft page is required")

    print("RESULT:")

    if problems:
        print("CHRIS REVIEW STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CHRIS REVIEW STATE: PASS")
    print("approved_for_draft_pages:", len(data["approved_for_draft_pages"]))
    print("next_required_gate: draft_approved_product_pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Validate pasted cloud product review results.

Read-only doctor.
No product page edits, affiliate links, commits, or pushes.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/product_review/research_results/batch_01_cloud_review_results.json"


def main() -> int:
    """Validate Batch 01 cloud review result locks."""
    problems: list[str] = []

    if not RESULTS.is_file():
        problems.append(f"missing results file: {RESULTS}")
    else:
        data = json.loads(RESULTS.read_text(encoding="utf-8"))

        expected = {
            "batch": 1,
            "status": "cloud_product_research_completed",
            "research_only": True,
            "ready_for_chris_review": True,
            "affiliate_links_created": False,
            "publish_recommended": False,
            "git_commit_allowed": False,
            "git_push_allowed": False,
            "next_required_gate": "chris_product_candidate_review",
        }

        for key, value in expected.items():
            if data.get(key) != value:
                problems.append(f"{key} expected {value!r}, got {data.get(key)!r}")

        slots = data.get("slots", [])

        if len(slots) != 6:
            problems.append(f"expected 6 reviewed slots, found {len(slots)}")

        for slot in slots:
            if not slot.get("recommended_candidates"):
                problems.append(f"slot {slot.get('slot')} has no candidates")

    print("RESULT:")

    if problems:
        print("CLOUD REVIEW RESULTS STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CLOUD REVIEW RESULTS STATE: PASS")
    print("batch: 1")
    print("reviewed_slots: 6")
    print("next_required_gate: chris_product_candidate_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

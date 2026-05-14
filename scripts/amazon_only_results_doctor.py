"""
Validate Amazon-only product research results.

Read-only doctor.
No affiliate links, product swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/product_review/research_results/batch_01_amazon_only_results.json"


def main() -> int:
    """Validate Amazon-only Batch 01 research results."""
    problems: list[str] = []

    if not RESULTS.is_file():
        problems.append(f"missing results file: {RESULTS}")
    else:
        data = json.loads(RESULTS.read_text(encoding="utf-8"))

        expected = {
            "batch": 1,
            "status": "amazon_only_product_research_completed",
            "amazon_only": True,
            "research_only": True,
            "ready_for_chris_review": True,
            "affiliate_links_created": False,
            "publish_recommended": False,
            "git_commit_allowed": False,
            "git_push_allowed": False,
            "next_required_gate": "chris_amazon_product_candidate_review",
        }

        for key, value in expected.items():
            if data.get(key) != value:
                problems.append(f"{key} expected {value!r}, got {data.get(key)!r}")

        slots = data.get("slots", [])

        if len(slots) != 6:
            problems.append(f"expected 6 slots, found {len(slots)}")

        for slot in slots:
            for candidate in slot.get("recommended_candidates", []):
                url = candidate.get("amazon_url", "")

                if "amazon.com" not in url:
                    problems.append(f"{slot.get('slug')}: non-Amazon URL found: {url}")

                if candidate.get("live_eligible_after_chris_affiliate_link_review") is not False:
                    problems.append(f"{slot.get('slug')}: live eligibility must remain false")

    print("RESULT:")

    if problems:
        print("AMAZON-ONLY RESULTS STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("AMAZON-ONLY RESULTS STATE: PASS")
    print("reviewed_slots: 6")
    print("next_required_gate: chris_amazon_product_candidate_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Validate candidate factory report.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "product_candidates" / "candidate_factory_report.json"


def main() -> int:
    """Validate candidate factory safety locks."""
    problems: list[str] = []

    if not REPORT.is_file():
        problems.append("missing candidate factory report")
    else:
        data = json.loads(REPORT.read_text(encoding="utf-8"))

        if not str(data.get("status", "")).startswith("candidate_factory_"):
            problems.append(f"invalid status: {data.get('status')}")

        for locked in [
            "affiliate_link_changes_allowed",
            "product_swap_allowed",
            "git_commit_allowed",
            "git_push_allowed",
            "publish_allowed",
        ]:
            if data.get(locked) is not False:
                problems.append(f"{locked} must be false")

    print("RESULT:")

    if problems:
        print("CANDIDATE FACTORY STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CANDIDATE FACTORY STATE: PASS")
    print("next_required_gate: review_candidate_factory_report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Validate rotation decision report.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "rotation" / "rotation_decision_report.json"


def main() -> int:
    """Validate rotation report locks."""
    problems: list[str] = []

    if not REPORT.is_file():
        problems.append(f"missing report: {REPORT}")
    else:
        data = json.loads(REPORT.read_text(encoding="utf-8"))

        if data.get("decision_count") != 24:
            problems.append(f"expected 24 decisions, got {data.get('decision_count')}")

        for key in [
            "replacement_allowed",
            "product_swap_allowed",
            "affiliate_link_changes_allowed",
            "git_commit_allowed",
            "git_push_allowed",
            "publish_allowed",
        ]:
            if data.get(key) is not False:
                problems.append(f"{key} must be false")

    print("RESULT:")

    if problems:
        print("ROTATION DECISION STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("ROTATION DECISION STATE: PASS")
    print("decision_count: 24")
    print("next_required_gate: rotation_decision_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

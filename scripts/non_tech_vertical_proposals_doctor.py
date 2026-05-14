"""
Validate non-tech vertical proposals.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSALS = ROOT / "data/site_portfolio/non_tech_vertical_proposals.json"


def main() -> int:
    """Validate non-tech vertical proposal state."""
    problems: list[str] = []

    if not PROPOSALS.is_file():
        problems.append("missing non-tech vertical proposals")
    else:
        data = json.loads(PROPOSALS.read_text(encoding="utf-8"))

        if data.get("status") != "vertical_proposals_ready":
            problems.append(f"bad status: {data.get('status')}")

        if data.get("proposal_count", 0) < 3:
            problems.append("expected at least 3 non-tech vertical proposals")

        for proposal in data.get("proposals", []):
            if not proposal.get("vertical_slug"):
                problems.append("proposal missing vertical_slug")

            if proposal.get("cloud_research_required") is not True:
                problems.append(f"{proposal.get('vertical_slug')}: cloud research must be required")

            if proposal.get("human_approval_required") is not True:
                problems.append(f"{proposal.get('vertical_slug')}: human approval must be required")

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
        print("NON-TECH VERTICAL PROPOSALS STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("NON-TECH VERTICAL PROPOSALS STATE: PASS")
    print("next_required_gate: cloud_ai_vertical_product_research")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

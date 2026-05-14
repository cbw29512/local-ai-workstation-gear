"""
Validate local candidate proposal.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "data" / "product_candidates" / "local_candidate_proposal.json"
CLOUD_PACKET = ROOT / "reports" / "product_candidates" / "cloud_clarification_packet.md"


def main() -> int:
    """Validate proposal state."""
    problems: list[str] = []

    if not PROPOSAL.is_file():
        problems.append("missing local candidate proposal")
    else:
        data = json.loads(PROPOSAL.read_text(encoding="utf-8"))

        if data.get("status") != "local_candidate_proposed":
            problems.append(f"proposal not ready: {data.get('status')}")

        if not data.get("recommended_candidates"):
            problems.append("proposal has no candidates")

        for locked in [
            "affiliate_link_changes_allowed",
            "product_swap_allowed",
            "git_commit_allowed",
            "git_push_allowed",
            "publish_allowed",
        ]:
            if data.get(locked) is not False:
                problems.append(f"{locked} must be false")

    if not CLOUD_PACKET.is_file():
        problems.append("missing cloud clarification packet")

    print("RESULT:")

    if problems:
        print("CANDIDATE PROPOSAL STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CANDIDATE PROPOSAL STATE: PASS")
    print("next_required_gate: cloud_ai_candidate_clarification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

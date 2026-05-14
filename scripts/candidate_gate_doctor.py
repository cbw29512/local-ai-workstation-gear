"""
Validate candidate gate resolver.

Read-only doctor.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.candidate_gate_status import resolve_candidate_gate


VALID_GATES = {
    "generate_local_candidate_proposal",
    "cloud_ai_candidate_clarification",
    "cloud_ai_candidate_needs_rework",
    "chris_affiliate_url_for_approved_candidate",
    "enable_next_approved_link",
}


def main() -> int:
    """Validate resolved candidate gate."""
    problems: list[str] = []
    gate = resolve_candidate_gate()

    if gate.get("status") != "candidate_gate_resolved":
        problems.append("bad resolver status")

    if gate.get("current_gate") not in VALID_GATES:
        problems.append(f"invalid gate: {gate.get('current_gate')}")

    for locked in [
        "affiliate_link_changes_allowed",
        "product_swap_allowed",
        "git_commit_allowed",
        "git_push_allowed",
        "publish_allowed",
    ]:
        if gate.get(locked) is not False:
            problems.append(f"{locked} must be false")

    print("RESULT:")

    if problems:
        print("CANDIDATE GATE STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CANDIDATE GATE STATE: PASS")
    print(f"current_gate: {gate['current_gate']}")
    print(f"slug: {gate.get('slug')}")
    print(f"reason: {gate['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

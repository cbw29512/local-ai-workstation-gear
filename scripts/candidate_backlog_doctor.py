"""
Validate candidate backlog.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "data" / "product_candidates" / "candidate_backlog.json"


def main() -> int:
    """Validate backlog state."""
    problems: list[str] = []

    if not BACKLOG.is_file():
        problems.append("missing candidate backlog")
    else:
        data = json.loads(BACKLOG.read_text(encoding="utf-8"))
        items = data.get("items", [])
        slugs = [item.get("slug") for item in items]

        if data.get("status") != "candidate_backlog_created":
            problems.append(f"bad status: {data.get('status')}")

        if len(slugs) != len(set(slugs)):
            problems.append("duplicate backlog slugs found")

        if data.get("current_gate_slug") in set(slugs):
            problems.append("backlog includes current pending gate slug")

        for item in items:
            if not item.get("recommended_candidates"):
                problems.append(f"{item.get('slug')}: missing candidates")

            if not Path(item.get("cloud_packet", "")).is_file():
                problems.append(f"{item.get('slug')}: missing durable cloud packet")

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
        print("CANDIDATE BACKLOG STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CANDIDATE BACKLOG STATE: PASS")
    print("next_required_gate: cloud_ai_backlog_clarification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Validate cloud vertical research packets.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/site_portfolio/cloud_vertical_research_queue.json"


def main() -> int:
    """Validate cloud vertical research queue."""
    problems: list[str] = []

    if not QUEUE.is_file():
        problems.append("missing cloud vertical research queue")
    else:
        data = json.loads(QUEUE.read_text(encoding="utf-8"))

        if data.get("status") != "cloud_vertical_research_queue_ready":
            problems.append(f"bad status: {data.get('status')}")

        if data.get("vertical_count", 0) < 3:
            problems.append("expected at least 3 vertical packets")

        for item in data.get("verticals", []):
            path = Path(item.get("packet_path", ""))

            if not path.is_file():
                problems.append(f"{item.get('vertical_slug')}: packet file missing")

            if item.get("cloud_research_required") is not True:
                problems.append(f"{item.get('vertical_slug')}: cloud research must be required")

            if item.get("human_approval_required") is not True:
                problems.append(f"{item.get('vertical_slug')}: human approval must be required")

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
        print("CLOUD VERTICAL RESEARCH PACKETS STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CLOUD VERTICAL RESEARCH PACKETS STATE: PASS")
    print("next_required_gate: cloud_ai_vertical_product_research")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

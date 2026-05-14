"""
Validate active cloud vertical research handoff.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "data/site_portfolio/cloud_vertical_handoff.json"


def main() -> int:
    """Validate handoff file."""
    problems: list[str] = []

    if not HANDOFF.is_file():
        problems.append("missing cloud vertical handoff")
    else:
        data = json.loads(HANDOFF.read_text(encoding="utf-8"))

        if data.get("status") != "cloud_vertical_handoff_ready":
            problems.append(f"bad status: {data.get('status')}")

        if not Path(data.get("source_packet", "")).is_file():
            problems.append("source packet file missing")

        if data.get("required_result_count") != 24:
            problems.append("required_result_count must be 24")

        rules = data.get("rules", {})
        if rules.get("no_affiliate_links_created") is not True:
            problems.append("no_affiliate_links_created must be true")

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
        print("CLOUD VERTICAL HANDOFF STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CLOUD VERTICAL HANDOFF STATE: PASS")
    print("next_required_gate: paste_cloud_vertical_research_results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

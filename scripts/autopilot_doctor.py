"""
Validate local AI autopilot output.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "webmaster" / "autopilot_next_action.json"
REPORT_MD = ROOT / "reports" / "webmaster" / "autopilot_next_action.md"
CLOUD_HANDOFF = ROOT / "reports" / "cloud_handoff" / "next_cloud_task.md"


def main() -> int:
    """Run autopilot doctor."""
    problems: list[str] = []

    for path in [REPORT_JSON, REPORT_MD, CLOUD_HANDOFF]:
        if not path.is_file():
            problems.append(f"missing file: {path}")

    if REPORT_JSON.is_file():
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

        false_keys = [
            "affiliate_link_changes_allowed",
            "product_swap_allowed",
            "git_commit_allowed",
            "git_push_allowed",
            "publish_allowed",
        ]

        for key in false_keys:
            if report.get(key) is not False:
                problems.append(f"{key} must be false")

        pipeline = report.get("product_pipeline", {})

        if pipeline.get("item_count") != 24:
            problems.append("item_count must be 24")

        if pipeline.get("product_packet_count") != 24:
            problems.append("product_packet_count must be 24")

    print("RESULT:")

    if problems:
        print("AUTOPILOT STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("AUTOPILOT STATE: PASS")
    print("Local AI webmaster autopilot is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

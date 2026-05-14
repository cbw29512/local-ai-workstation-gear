"""
Validate money monitor output.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "money_monitor" / "money_status.json"


def main() -> int:
    """Validate money monitor report."""
    problems: list[str] = []

    if not REPORT.is_file():
        problems.append(f"missing report: {REPORT}")
    else:
        data = json.loads(REPORT.read_text(encoding="utf-8"))

        if data.get("status") != "money_monitor_ready":
            problems.append("invalid money monitor status")

        for key in [
            "affiliate_link_changes_allowed",
            "product_swap_allowed",
            "git_commit_allowed",
            "git_push_allowed",
            "publish_allowed",
        ]:
            if data.get(key) is not False:
                problems.append(f"{key} must be false")

        if data.get("live_amazon_links", 0) < 1:
            problems.append("expected at least one live Amazon link")

    print("RESULT:")

    if problems:
        print("MONEY MONITOR STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("MONEY MONITOR STATE: PASS")
    print("next_required_gate: monitor_affiliate_clicks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

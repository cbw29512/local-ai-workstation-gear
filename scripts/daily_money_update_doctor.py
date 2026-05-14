"""
Validate daily money update report.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "money_monitor" / "daily_money_update.json"


def main() -> int:
    """Validate daily money report."""
    problems: list[str] = []

    if not REPORT.is_file():
        problems.append("missing daily money update report")
    else:
        data = json.loads(REPORT.read_text(encoding="utf-8"))

        if data.get("status") != "daily_money_update_completed":
            problems.append(f"bad status: {data.get('status')}")

        if data.get("live_amazon_links", 0) < 1:
            problems.append("expected at least one live Amazon link")

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
        print("DAILY MONEY UPDATE DOCTOR: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("DAILY MONEY UPDATE DOCTOR: PASS")
    print("next_required_gate: monitor_affiliate_clicks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

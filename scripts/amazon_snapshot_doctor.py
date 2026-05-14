"""
Validate Amazon metrics snapshot baseline.

Read-only doctor.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "data" / "performance" / "amazon_click_snapshots.json"


def is_iso(value: str | None) -> bool:
    """Validate ISO timestamp text."""
    if not value:
        return False

    try:
        datetime.fromisoformat(value)
        return True
    except Exception:
        return False


def main() -> int:
    """Validate snapshot baseline."""
    problems: list[str] = []

    if not SNAPSHOTS.is_file():
        problems.append("missing amazon_click_snapshots.json")
    else:
        data = json.loads(SNAPSHOTS.read_text(encoding="utf-8"))
        rows = data.get("snapshots", [])

        if not rows:
            problems.append("snapshot rows are empty")

        for row in rows:
            slug = row.get("slug", "unknown")

            if not is_iso(row.get("captured_at")):
                problems.append(f"{slug}: captured_at missing or invalid")

            for key in ["clicks_30d", "affiliate_clicks_30d", "impressions_30d"]:
                if int(row.get(key, -1)) < 0:
                    problems.append(f"{slug}: {key} cannot be negative")

        for locked in [
            "replacement_allowed",
            "product_swap_allowed",
            "affiliate_link_changes_allowed",
            "git_commit_allowed",
            "git_push_allowed",
            "publish_allowed",
        ]:
            if data.get(locked) is not False:
                problems.append(f"{locked} must be false")

    print("RESULT:")

    if problems:
        print("AMAZON SNAPSHOT STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("AMAZON SNAPSHOT STATE: PASS")
    print("next_required_gate: monitor_affiliate_clicks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

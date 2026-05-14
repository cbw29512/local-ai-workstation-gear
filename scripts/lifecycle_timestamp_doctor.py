"""
Validate lifecycle timestamps.

Read-only doctor.
No affiliate links, product swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE_JSON = ROOT / "data" / "item_lifecycle.json"


REQUIRED_ITEM_FIELDS = [
    "slot",
    "slug",
    "first_seen_at",
    "last_reviewed_at",
    "next_review_at",
    "rotation_due_at",
    "rotation_status",
    "replacement_allowed",
]


def valid_iso(value: str | None) -> bool:
    """Validate ISO timestamp when present."""
    if value is None:
        return True

    try:
        datetime.fromisoformat(value)
        return True
    except Exception:
        return False


def main() -> int:
    """Run lifecycle timestamp doctor."""
    problems: list[str] = []

    if not LIFECYCLE_JSON.is_file():
        problems.append(f"missing lifecycle file: {LIFECYCLE_JSON}")
    else:
        data = json.loads(LIFECYCLE_JSON.read_text(encoding="utf-8"))
        items = data.get("items", [])

        if data.get("status") != "item_lifecycle_timestamped":
            problems.append("invalid lifecycle status")

        if data.get("item_count") != 24:
            problems.append(f"expected item_count 24, got {data.get('item_count')}")

        if len(items) != 24:
            problems.append(f"expected 24 lifecycle items, found {len(items)}")

        for item in items:
            slug = item.get("slug", "unknown")

            for field in REQUIRED_ITEM_FIELDS:
                if field not in item:
                    problems.append(f"{slug}: missing {field}")

            for field in [
                "first_seen_at",
                "first_live_at",
                "last_reviewed_at",
                "next_review_at",
                "rotation_due_at",
                "last_optimized_at",
                "last_replaced_at",
                "protected_at",
            ]:
                if not valid_iso(item.get(field)):
                    problems.append(f"{slug}: invalid timestamp {field}")

            for locked in [
                "replacement_allowed",
                "affiliate_link_changes_allowed",
                "product_swap_allowed",
                "git_commit_allowed",
                "git_push_allowed",
                "publish_allowed",
            ]:
                if item.get(locked) is not False:
                    problems.append(f"{slug}: {locked} must be false")

    print("RESULT:")

    if problems:
        print("LIFECYCLE TIMESTAMP STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("LIFECYCLE TIMESTAMP STATE: PASS")
    print("item_count: 24")
    print("next_required_gate: lifecycle_timestamp_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

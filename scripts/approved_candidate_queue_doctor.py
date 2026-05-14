"""
Validate approved candidate queue.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/product_candidates/approved_candidate_queue.json"


def main() -> int:
    """Validate approved queue safety and content."""
    problems: list[str] = []

    if not QUEUE.is_file():
        problems.append("missing approved candidate queue")
    else:
        data = json.loads(QUEUE.read_text(encoding="utf-8"))

        if data.get("status") != "approved_candidate_queue_ready":
            problems.append(f"bad queue status: {data.get('status')}")

        if data.get("approved_count", 0) < 1:
            problems.append("expected at least one approved item")

        for item in data.get("approved_items", []):
            slug = item.get("slug", "unknown")

            if not item.get("asin"):
                problems.append(f"{slug}: missing ASIN")

            url = str(item.get("amazon_url", ""))
            if "amazon.com" not in url and "amzn.to" not in url:
                problems.append(f"{slug}: URL must be Amazon/amzn.to")

            if item.get("approved_by_chris") is not False:
                problems.append(f"{slug}: approved_by_chris must remain false")

            if item.get("live_enabled") is not False:
                problems.append(f"{slug}: live_enabled must remain false")

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
        print("APPROVED CANDIDATE QUEUE STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("APPROVED CANDIDATE QUEUE STATE: PASS")
    print("next_required_gate: chris_affiliate_url_for_approved_candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

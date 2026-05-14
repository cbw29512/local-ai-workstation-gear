"""
Validate backlog cloud clarification decisions.

State:
- Backlog candidates may be approve, hold, or replace.
- Approval does not mean live publishing.
- Chris still must provide/approve affiliate URLs.

Safety:
- Read-only doctor.
- No affiliate links.
- No swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLARIFICATIONS = ROOT / "data/product_candidates/backlog_cloud_clarifications.json"
LOG_FILE = ROOT / "logs/backlog_cloud_clarification_doctor.log"


VALID_DECISIONS = {"approve", "hold", "replace"}


def setup_logging() -> None:
    """Create doctor log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict:
    """Load JSON with clear failure context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def validate_item(item: dict) -> list[str]:
    """Validate one clarification item."""
    problems: list[str] = []
    slug = item.get("slug", "unknown")

    if item.get("final_decision") not in VALID_DECISIONS:
        problems.append(f"{slug}: invalid final_decision")

    if not item.get("best_candidate_asin"):
        problems.append(f"{slug}: missing ASIN")

    url = str(item.get("best_candidate_amazon_url", ""))
    if "amazon.com" not in url and "amzn.to" not in url:
        problems.append(f"{slug}: candidate URL must be Amazon/amzn.to")

    for locked in ["affiliate_links_created", "approved_by_chris", "live_enabled"]:
        if item.get(locked) is not False:
            problems.append(f"{slug}: {locked} must be false")

    return problems


def main() -> int:
    """Run backlog clarification doctor."""
    setup_logging()
    problems: list[str] = []

    try:
        data = load_json(CLARIFICATIONS)
    except Exception as exc:
        print("RESULT:")
        print("BACKLOG CLOUD CLARIFICATION STATE: NEEDS REVIEW")
        print(f"- {exc}")
        return 1

    if data.get("status") != "backlog_cloud_clarified":
        problems.append("bad clarification status")

    items = data.get("items", [])
    if len(items) < 1:
        problems.append("no clarification items found")

    for item in items:
        problems.extend(validate_item(item))

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
        print("BACKLOG CLOUD CLARIFICATION STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    approved = sum(1 for item in items if item.get("final_decision") == "approve")
    held = sum(1 for item in items if item.get("final_decision") == "hold")

    print("BACKLOG CLOUD CLARIFICATION STATE: PASS")
    print(f"clarified_items: {len(items)}")
    print(f"approved_items: {approved}")
    print(f"held_items: {held}")
    print("next_required_gate: chris_affiliate_url_for_approved_backlog_candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

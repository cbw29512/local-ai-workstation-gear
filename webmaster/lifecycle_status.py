"""
Lifecycle status reader for autopilot.

Read-only:
- No edits.
- No affiliate links.
- No product swaps.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from webmaster.lifecycle_paths import LIFECYCLE_JSON


def parse_time(value: str | None) -> datetime | None:
    """Parse ISO timestamps when present."""
    if value is None:
        return None

    return datetime.fromisoformat(value)


def load_lifecycle() -> dict[str, Any]:
    """Load lifecycle file if it exists."""
    if not LIFECYCLE_JSON.is_file():
        return {"items": []}

    return json.loads(LIFECYCLE_JSON.read_text(encoding="utf-8"))


def build_lifecycle_status() -> dict[str, Any]:
    """Summarize lifecycle timing for autopilot."""
    lifecycle = load_lifecycle()
    now = datetime.now(timezone.utc)
    items = lifecycle.get("items", [])

    due_review = []
    due_rotation = []
    protected = []

    for item in items:
        next_review = parse_time(item.get("next_review_at"))
        rotation_due = parse_time(item.get("rotation_due_at"))

        if next_review and next_review <= now:
            due_review.append(item["slug"])

        if rotation_due and rotation_due <= now:
            due_rotation.append(item["slug"])

        if item.get("rotation_status") == "protected_winner":
            protected.append(item["slug"])

    return {
        "lifecycle_exists": LIFECYCLE_JSON.is_file(),
        "lifecycle_item_count": len(items),
        "due_for_review_count": len(due_review),
        "due_for_rotation_count": len(due_rotation),
        "protected_winner_count": len(protected),
        "due_for_review": due_review,
        "due_for_rotation": due_rotation,
        "protected_winners": protected,
    }

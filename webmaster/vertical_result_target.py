"""
Resolve active vertical research result target.

State:
- Reads active cloud vertical handoff when present.
- Falls back to home-organization intake.
"""

from __future__ import annotations

from pathlib import Path

from webmaster.vertical_result_io import load_json
from webmaster.vertical_result_paths import FALLBACK_RESULT, HANDOFF


def active_target() -> tuple[str, Path]:
    """Return active vertical slug and target result path."""
    if not HANDOFF.is_file():
        return "home-organization", FALLBACK_RESULT

    handoff = load_json(HANDOFF)
    slug = str(handoff.get("vertical_slug", "home-organization"))
    target = Path(str(handoff.get("target_result_file", FALLBACK_RESULT)))

    return slug, target

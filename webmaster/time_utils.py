"""
Timestamp helpers for the local AI webmaster.

State first:
- All machine timestamps use UTC ISO-8601.
- Human display can convert later.
- UTC avoids confusion when launchd, GitHub Pages, and cloud review run in different contexts.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utc_now_iso() -> str:
    """Return current UTC time as ISO-8601 text."""
    return datetime.now(timezone.utc).isoformat()


def add_days_iso(source_iso: str, days: int) -> str:
    """Add days to an existing ISO timestamp."""
    source = datetime.fromisoformat(source_iso)
    return (source + timedelta(days=days)).isoformat()

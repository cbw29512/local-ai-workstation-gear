"""
Money monitor IO helpers.

Local read-only helpers for monitor inputs.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from webmaster.money_paths import LOG_FILE


def setup_logging() -> None:
    """Create money monitor logging."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    """Load JSON or return fallback if missing/broken."""
    try:
        if not path.is_file():
            return fallback

        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        return fallback

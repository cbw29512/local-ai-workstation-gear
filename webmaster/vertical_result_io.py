"""
Vertical result IO helpers.

Safety:
- Read-only helpers for doctor logic.
- No affiliate links.
- No product swaps.
- No publishing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from webmaster.vertical_result_paths import LOG_FILE


def setup_logging() -> None:
    """Create doctor log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with useful failure context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise

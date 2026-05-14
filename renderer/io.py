"""
Renderer IO helpers.

Local-only file reads/writes with logging.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from renderer.paths import DATA_FILE, LOG_FILE


def setup_logging() -> None:
    """Create logging for render failures."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_inventory() -> dict[str, Any]:
    """Load item inventory safely."""
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load inventory: %s", exc)
        raise


def write_text(path: Path, text: str) -> None:
    """Write one text file safely."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write %s: %s", path, exc)
        raise

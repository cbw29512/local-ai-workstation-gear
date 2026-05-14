"""
Candidate proposal IO helpers.

Local reads/writes only.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from webmaster.candidate_paths import LOG_FILE


def setup_logging() -> None:
    """Create candidate proposal logging."""
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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON safely."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write %s: %s", path, exc)
        raise


def write_text(path: Path, text: str) -> None:
    """Write text safely."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write %s: %s", path, exc)
        raise

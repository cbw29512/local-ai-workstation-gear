"""
IO helpers for the local AI webmaster supervisor.

All helpers are local only.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from webmaster.paths import LOG_DIR, LOG_FILE


def setup_logging() -> None:
    """Create local logging so every run is traceable."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with useful error logging."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load JSON from %s: %s", path, exc)
        raise


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON safely in readable format."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write JSON to %s: %s", path, exc)
        raise


def write_text(path: Path, text: str) -> None:
    """Write text safely."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write text to %s: %s", path, exc)
        raise

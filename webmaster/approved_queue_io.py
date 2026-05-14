"""
Approved candidate queue IO helpers.

Safety:
- Local reads/writes only.
- No affiliate links, product swaps, publishing, commits, or pushes.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from webmaster.approved_queue_paths import LOG_FILE


def setup_logging() -> None:
    """Create queue generation log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_optional(path: Path) -> dict[str, Any]:
    """Load optional JSON file."""
    if not path.is_file():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def write_text(path: Path, content: str) -> None:
    """Write text with useful error context."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write %s: %s", path, exc)
        raise


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON with deterministic formatting."""
    write_text(path, json.dumps(payload, indent=2))

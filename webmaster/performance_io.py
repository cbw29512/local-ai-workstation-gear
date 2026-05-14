"""
Performance IO helpers.

Local file reads/writes only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with a useful error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to load {path}: {exc}") from exc


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON in readable format."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Failed to write {path}: {exc}") from exc


def write_text(path: Path, text: str) -> None:
    """Write text with useful failure context."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Failed to write {path}: {exc}") from exc

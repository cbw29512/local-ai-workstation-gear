"""
Vertical workflow audit checks.

State:
- Prompt is for large/cloud AI.
- Staged JSON is where returned cloud JSON is pasted.
- Active result is what validation checks.

Safety:
- Read-only checks.
- No affiliate links, swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from webmaster.vertical_workflow_paths import ACTIVE, HANDOFF, LOG_FILE, PROMPT, STAGED


def setup_logging() -> None:
    """Create audit log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Load JSON and return data or error text."""
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        return None, str(exc)


def prompt_problems() -> list[str]:
    """Audit the active prompt file."""
    if not PROMPT.is_file():
        return [f"missing prompt: {PROMPT}"]

    text = PROMPT.read_text(encoding="utf-8")
    markers = [
        "Return ONE raw JSON object only",
        "The items array must contain exactly 24 objects",
        "vertical_slug",
        "cloud_vertical_research_completed",
    ]

    return [f"prompt missing marker: {marker}" for marker in markers if marker not in text]


def handoff_problems() -> list[str]:
    """Audit handoff and target path."""
    if not HANDOFF.is_file():
        return [f"missing handoff: {HANDOFF}"]

    data, error = load_json(HANDOFF)

    if error or data is None:
        return [f"handoff invalid JSON: {error}"]

    problems: list[str] = []

    if data.get("status") != "cloud_vertical_handoff_ready":
        problems.append(f"handoff bad status: {data.get('status')}")

    if data.get("vertical_slug") != "home-organization":
        problems.append(f"handoff vertical mismatch: {data.get('vertical_slug')}")

    if Path(str(data.get("target_result_file", ""))) != ACTIVE:
        problems.append(f"handoff target mismatch: {data.get('target_result_file')}")

    return problems


def result_summary(path: Path) -> tuple[list[str], dict[str, Any]]:
    """Audit one result JSON file and return summary fields."""
    summary: dict[str, Any] = {"path": str(path), "exists": path.is_file()}
    summary.update({"status": None, "vertical_slug": None, "items": None})

    if not path.is_file():
        return [f"missing result file: {path}"], summary

    data, error = load_json(path)

    if error or data is None:
        return [f"{path.name}: invalid JSON: {error}"], summary

    items = data.get("items", [])
    summary.update(
        {
            "status": data.get("status"),
            "vertical_slug": data.get("vertical_slug"),
            "items": len(items),
        }
    )

    problems: list[str] = []

    if data.get("vertical_slug") != "home-organization":
        problems.append(f"{path.name}: vertical_slug must be home-organization")

    if data.get("status") == "cloud_vertical_research_completed" and len(items) != 24:
        problems.append(f"{path.name}: completed result must have 24 items")

    return problems, summary


def gather_audit_state() -> tuple[list[str], dict[str, Any], dict[str, Any]]:
    """Gather all workflow problems and summaries."""
    setup_logging()
    problems: list[str] = []
    problems.extend(prompt_problems())
    problems.extend(handoff_problems())

    staged_problems, staged = result_summary(STAGED)
    active_problems, active = result_summary(ACTIVE)

    problems.extend(staged_problems)
    problems.extend(active_problems)

    return problems, staged, active

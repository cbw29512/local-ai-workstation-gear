"""
Daily money update command runner.

Safety:
- Runs local doctors and reports only.
- No affiliate link changes, swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any


COMMANDS = [
    ["python3", "scripts/amazon_link_registry_doctor.py"],
    ["python3", "scripts/live_money_state_doctor.py"],
    ["python3", "scripts/amazon_snapshot_doctor.py"],
    ["python3", "scripts/import_manual_amazon_metrics.py"],
    ["python3", "scripts/run_rotation_decisions.py"],
    ["python3", "scripts/money_monitor_run_once.py"],
    ["python3", "scripts/money_monitor_doctor.py"],
    ["python3", "scripts/rotation_decision_doctor.py"],
]


def run_command(root: Path, command: list[str]) -> dict[str, Any]:
    """Run one command and capture its result."""
    try:
        result = subprocess.run(
            command,
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        return {
            "command": " ".join(command),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0,
        }
    except Exception as exc:
        logging.exception("Command failed to execute: %s", command)
        return {
            "command": " ".join(command),
            "returncode": 1,
            "stdout": "",
            "stderr": str(exc),
            "passed": False,
        }

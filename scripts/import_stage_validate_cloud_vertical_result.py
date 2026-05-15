"""
Safely import, stage, and validate cloud vertical research result.

State:
- Imports cloud JSON from clipboard.
- Stops if clipboard import fails.
- Stages only after import succeeds.
- Validates active result only after staging succeeds.

Safety:
- No affiliate links.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / "logs/import_stage_validate_cloud_vertical_result.log"


COMMANDS = [
    ["python3", "scripts/import_clipboard_cloud_vertical_result.py"],
    ["python3", "scripts/stage_cloud_vertical_result.py"],
    ["python3", "scripts/cloud_vertical_result_doctor.py"],
]


def setup_logging() -> None:
    """Create orchestration log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def run_command(command: list[str]) -> int:
    """Run one command and print its output."""
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except Exception as exc:
        logging.exception("Failed to execute %s: %s", command, exc)
        print(f"COMMAND ERROR: {' '.join(command)}")
        print(exc)
        return 1

    if result.stdout:
        print(result.stdout.strip())

    if result.stderr:
        print(result.stderr.strip())

    return result.returncode


def main() -> int:
    """Run safe import/stage/validate workflow."""
    setup_logging()

    for command in COMMANDS:
        code = run_command(command)

        if code != 0:
            print("RESULT: STOPPED")
            print(f"failed_command: {' '.join(command)}")
            print("No later steps were run.")
            return code

    print("RESULT: PASS")
    print("next_required_gate: chris_vertical_site_approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

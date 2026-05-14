"""
Path constants for the local AI webmaster supervisor.

State first:
- This module defines file paths only.
- It performs no file edits, commits, pushes, or external actions.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "reports" / "webmaster"
LOG_DIR = ROOT / "logs"

ITEMS_JSON = DATA_DIR / "items.json"
STATE_JSON = DATA_DIR / "webmaster_state.json"

LATEST_JSON = REPORT_DIR / "latest_supervisor_report.json"
LATEST_MD = REPORT_DIR / "latest_supervisor_report.md"

LOG_FILE = LOG_DIR / "local_ai_webmaster.log"

"""
Renderer path constants.

State first:
- Defines local file paths only.
- No git add, commit, push, GitHub API, credentials, DNS, or external actions.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "items.json"
LOG_FILE = ROOT / "reports" / "render_public_pages.log"

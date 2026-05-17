"""
Site health path constants.

State:
- Paths only.
- No publishing, commits, pushes, swaps, or affiliate changes.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
REPORT_JSON = ROOT / "reports/site_webmaster/latest_site_webmaster_report.json"
REPORT_MD = ROOT / "reports/site_webmaster/latest_site_webmaster_report.md"
LOG_FILE = ROOT / "logs/hourly_site_webmaster_operator.log"

"""
Audit public-facing static files for branding and funnel/page structure.

State schema:
{
  "wrong_brand_hits": list[str],
  "old_url_hits": list[str],
  "page_count": int,
  "site_page_count": int,
  "hub_count": int,
  "needs_review": bool
}

Safety:
- Read-only.
- No file edits.
- No git add, commit, or push.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/public_surface_audit.json"
LOG_FILE = ROOT / "reports/public_surface_audit.log"

WRONG_BRAND_PATTERNS = [
    "Home Depot Affiliate Engine",
    "Home Depot affiliate",
    "homedepotaffiliate",
    "Home Depot",
]

EXPECTED_PUBLIC_BRAND = "Local AI Workstation Gear"


def setup_logging() -> None:
    """Create an audit log for traceability."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def html_files() -> list[Path]:
    """Return public HTML files while ignoring Git internals."""
    try:
        return [
            path
            for path in ROOT.rglob("*.html")
            if ".git" not in path.parts
        ]
    except Exception as exc:
        logging.exception("Failed to list HTML files: %s", exc)
        raise


def scan_file(path: Path) -> tuple[list[str], list[str]]:
    """Scan one HTML file for wrong branding and old URLs."""
    wrong_brand_hits: list[str] = []
    old_url_hits: list[str] = []

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        logging.exception("Failed to read %s: %s", path, exc)
        return [f"{path}: read failed"], []

    for pattern in WRONG_BRAND_PATTERNS:
        if pattern in text:
            wrong_brand_hits.append(f"{path.relative_to(ROOT)} :: {pattern}")

    if "cbw29512.github.io/homedepotaffiliate" in text:
        old_url_hits.append(f"{path.relative_to(ROOT)} :: old homedepotaffiliate URL")

    return wrong_brand_hits, old_url_hits


def build_audit() -> dict[str, Any]:
    """Build the public surface audit from current static files."""
    wrong_brand_hits: list[str] = []
    old_url_hits: list[str] = []

    for path in html_files():
        brand_hits, url_hits = scan_file(path)
        wrong_brand_hits.extend(brand_hits)
        old_url_hits.extend(url_hits)

    page_files = list((ROOT / "pages").glob("*.html")) if (ROOT / "pages").is_dir() else []
    site_pages = list((ROOT / "sites").glob("*/index.html")) if (ROOT / "sites").is_dir() else []
    hubs = list((ROOT / "hubs").glob("*/index.html")) if (ROOT / "hubs").is_dir() else []

    return {
        "expected_public_brand": EXPECTED_PUBLIC_BRAND,
        "wrong_brand_hits": wrong_brand_hits,
        "old_url_hits": old_url_hits,
        "page_count": len(page_files),
        "site_page_count": len(site_pages),
        "hub_count": len(hubs),
        "target_page_count": 24,
        "needs_more_pages": len(site_pages) < 24,
        "needs_review": bool(wrong_brand_hits or old_url_hits or len(site_pages) < 24),
        "next_required_gate": "public_brand_and_inventory_patch",
    }


def main() -> int:
    """Run the read-only public surface audit."""
    setup_logging()

    try:
        audit = build_audit()
        REPORT.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS" if not audit["needs_review"] else "RESULT: NEEDS REVIEW")
    print(f"report: {REPORT}")
    print(f"wrong_brand_hits: {len(audit['wrong_brand_hits'])}")
    print(f"old_url_hits: {len(audit['old_url_hits'])}")
    print(f"site_page_count: {audit['site_page_count']}")
    print(f"target_page_count: {audit['target_page_count']}")
    print(f"next_required_gate: {audit['next_required_gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

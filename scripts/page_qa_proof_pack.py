"""
Page QA proof pack for live Amazon affiliate pages.

State:
- Reads approved live Amazon registry rows.
- Checks local site pages and redirect files.
- Prints local and GitHub Pages URLs for browser review.

Safety:
- Read-only.
- No page edits.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
PUBLIC_BASE_URL = "https://cbw29512.github.io/local-ai-workstation-gear"


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON safely."""
    return json.loads(path.read_text(encoding="utf-8"))


def redirect_slug(row: dict[str, Any]) -> str:
    """Build redirect slug."""
    slug = str(row.get("slug", ""))
    asin = str(row.get("asin") or "amazon")
    return f"{slug}-{asin}".lower()


def live_rows() -> list[dict[str, Any]]:
    """Return approved live registry rows."""
    registry = load_json(REGISTRY)
    return [
        row
        for row in registry.get("links", [])
        if row.get("approved_by_chris") is True
        and row.get("live_enabled") is True
    ]


def check_page(row: dict[str, Any]) -> dict[str, Any]:
    """Check one local page and redirect pair."""
    slug = str(row.get("slug", ""))
    asin = str(row.get("asin", ""))
    affiliate_url = str(row.get("affiliate_url") or "")
    approved_url = str(row.get("approved_affiliate_url") or "")
    redir = redirect_slug(row)

    site_path = ROOT / "sites" / slug / "index.html"
    docs_redirect = ROOT / "docs" / "out" / redir / "index.html"
    root_redirect = ROOT / "out" / redir / "index.html"

    problems: list[str] = []

    if not site_path.is_file():
        problems.append("missing site page")
        html = ""
    else:
        html = site_path.read_text(encoding="utf-8", errors="replace")

    markers = [affiliate_url, approved_url, redir, f"/out/{redir}", f"out/{redir}"]

    if html and not any(marker and marker in html for marker in markers):
        problems.append("page missing affiliate URL or redirect slug")

    if html and "PASTE_CHRIS_APPROVED" in html:
        problems.append("page still contains affiliate placeholder")

    if html and "Amazon Associate" not in html and "qualifying purchases" not in html:
        problems.append("page missing Amazon disclosure")

    if html and asin and asin not in html:
        problems.append("page missing ASIN")

    if not docs_redirect.is_file():
        problems.append("missing docs/out redirect")

    if not root_redirect.is_file():
        problems.append("missing out redirect")

    return {
        "slug": slug,
        "asin": asin,
        "status": "pass" if not problems else "needs_review",
        "problems": problems,
        "local_page": f"http://localhost:8787/sites/{slug}/",
        "local_redirect": f"http://localhost:8787/out/{redir}/",
        "public_page": f"{PUBLIC_BASE_URL}/sites/{slug}/",
        "public_redirect": f"{PUBLIC_BASE_URL}/out/{redir}/",
    }


def main() -> int:
    """Run page QA proof pack."""
    results = [check_page(row) for row in live_rows()]
    problem_count = sum(len(item["problems"]) for item in results)

    print("RESULT:")
    print("PAGE QA PROOF PACK")
    print(f"checked_pages: {len(results)}")
    print(f"problem_count: {problem_count}")

    for item in results:
        print("-" * 72)
        print(f"slug: {item['slug']}")
        print(f"asin: {item['asin']}")
        print(f"status: {item['status']}")
        print(f"local_page: {item['local_page']}")
        print(f"local_redirect: {item['local_redirect']}")
        print(f"public_page: {item['public_page']}")
        print(f"public_redirect: {item['public_redirect']}")

        for problem in item["problems"]:
            print(f"problem: {problem}")

    return 0 if problem_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

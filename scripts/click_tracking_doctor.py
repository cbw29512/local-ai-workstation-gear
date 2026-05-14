"""
Validate affiliate click tracking instrumentation.

Read-only doctor.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "assets" / "affiliate_clicks.js"
DOCS_ASSET = ROOT / "docs" / "assets" / "affiliate_clicks.js"
PAGE = ROOT / "sites" / "starter-local-ai-mini-pc" / "index.html"
DOCS_PAGE = ROOT / "docs" / "sites" / "starter-local-ai-mini-pc" / "index.html"


def has_required_tracking(text: str) -> bool:
    """Check required tracking attributes."""
    required = [
        'data-affiliate-click="amazon"',
        'data-merchant="amazon"',
        'data-slot="1"',
        'data-slug="starter-local-ai-mini-pc"',
        'data-asin="B0GHNDHGP5"',
        'affiliate_clicks.js',
    ]

    return all(item in text for item in required)


def main() -> int:
    """Validate click tracking files."""
    problems: list[str] = []

    if not ASSET.is_file():
        problems.append("missing assets/affiliate_clicks.js")

    if not DOCS_ASSET.is_file():
        problems.append("missing docs/assets/affiliate_clicks.js")

    for page in [PAGE, DOCS_PAGE]:
        if not page.is_file():
            problems.append(f"missing page: {page}")
            continue

        text = page.read_text(encoding="utf-8", errors="ignore")

        if not has_required_tracking(text):
            problems.append(f"{page.relative_to(ROOT)} missing tracking attributes")

    print("RESULT:")

    if problems:
        print("CLICK TRACKING STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CLICK TRACKING STATE: PASS")
    print("affiliate click attributes and script are present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

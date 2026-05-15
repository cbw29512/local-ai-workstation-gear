"""
Validate Amazon affiliate link registry.

State:
- Registry contains approved/staged Amazon product links.
- Live rows must have usable affiliate URLs.
- Staged rows may remain not live until page injection/publish gates pass.

Safety:
- Read-only doctor.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
LOG_FILE = ROOT / "logs/amazon_link_registry_doctor.log"
APPROVED_TAG = "maxyourheal06-20"


def setup_logging() -> None:
    """Create registry doctor log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with useful error context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def is_amazon_url(url: str) -> bool:
    """Return true for Amazon product URLs or Amazon short links."""
    return "amazon.com" in url or "amzn.to" in url


def validate_live_row(row: dict[str, Any]) -> list[str]:
    """Validate one live registry row."""
    problems: list[str] = []
    slug = row.get("slug", "unknown")
    url = str(row.get("affiliate_url") or "")
    asin = str(row.get("asin") or "")

    if row.get("approved_by_chris") is not True:
        problems.append(f"{slug}: live row must be approved_by_chris")

    if not asin:
        problems.append(f"{slug}: live row missing ASIN")

    if not url:
        problems.append(f"{slug}: live row missing affiliate_url")
        return problems

    if not is_amazon_url(url):
        problems.append(f"{slug}: live affiliate_url must be Amazon/amzn.to")

    if "amazon.com" in url and f"tag={APPROVED_TAG}" not in url:
        problems.append(f"{slug}: live affiliate_url missing approved tag")

    if asin and "amazon.com" in url and f"/dp/{asin}" not in url:
        problems.append(f"{slug}: live affiliate_url missing ASIN path")

    return problems


def validate_registry(data: dict[str, Any]) -> tuple[list[str], int, int]:
    """Validate registry and return problems plus counts."""
    problems: list[str] = []
    links = data.get("links", [])

    if not isinstance(links, list):
        return ["registry links must be a list"], 0, 0

    approved_live_links = 0

    for row in links:
        if row.get("live_enabled") is True:
            approved_live_links += 1
            problems.extend(validate_live_row(row))

    return problems, len(links), approved_live_links


def main() -> int:
    """Run Amazon link registry doctor."""
    setup_logging()

    try:
        data = load_json(REGISTRY)
        problems, registry_links, approved_live_links = validate_registry(data)
    except Exception as exc:
        print("RESULT:")
        print("AMAZON LINK REGISTRY STATE: NEEDS REVIEW")
        print(f"- {exc}")
        return 1

    print("RESULT:")

    if problems:
        print("AMAZON LINK REGISTRY STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("AMAZON LINK REGISTRY STATE: PASS")
    print(f"registry_links: {registry_links}")
    print(f"approved_live_links: {approved_live_links}")
    print("next_required_gate: inject_links_into_pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Validate generated affiliate links are live-enabled.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
APPROVED_TAG = "maxyourheal06-20"


def main() -> int:
    """Validate generated live links."""
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    problems: list[str] = []
    generated = [
        row for row in data.get("links", [])
        if row.get("generated_from_universal_tag") is True
    ]

    if len(generated) < 3:
        problems.append(f"expected at least 3 generated links, got {len(generated)}")

    for row in generated:
        slug = row.get("slug", "unknown")
        asin = str(row.get("asin") or "")
        url = str(row.get("affiliate_url") or "")

        if row.get("approved_by_chris") is not True:
            problems.append(f"{slug}: approved_by_chris must be true")

        if row.get("live_enabled") is not True:
            problems.append(f"{slug}: live_enabled must be true")

        if not url:
            problems.append(f"{slug}: missing affiliate_url")

        if asin and f"/dp/{asin}" not in url:
            problems.append(f"{slug}: affiliate_url missing ASIN path")

        if f"tag={APPROVED_TAG}" not in url:
            problems.append(f"{slug}: affiliate_url missing approved tag")

    print("RESULT:")

    if problems:
        print("LIVE GENERATED AFFILIATE LINKS STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("LIVE GENERATED AFFILIATE LINKS STATE: PASS")
    print(f"generated_live_links: {len(generated)}")
    print("next_required_gate: inject_links_into_pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

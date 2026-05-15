"""
Validate generated affiliate links were added to registry.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "data/amazon_links/generated_affiliate_links_from_queue.json"
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"


def load_json(path: Path) -> dict:
    """Load JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def registry_index(registry: dict) -> dict[tuple[str, str], dict]:
    """Index registry rows by slug and ASIN."""
    return {
        (str(row.get("slug", "")), str(row.get("asin", ""))): row
        for row in registry.get("links", [])
    }


def main() -> int:
    """Validate generated links are present in registry."""
    problems: list[str] = []

    generated = load_json(GENERATED)
    registry = load_json(REGISTRY)
    index = registry_index(registry)

    for source in generated.get("links", []):
        slug = str(source.get("slug", ""))
        asin = str(source.get("asin", ""))
        row = index.get((slug, asin))

        if row is None:
            problems.append(f"{slug}: missing from registry")
            continue

        url = str(row.get("affiliate_url", ""))

        if f"/dp/{asin}/" not in url:
            problems.append(f"{slug}: affiliate URL missing ASIN")

        if "tag=maxyourheal06-20" not in url:
            problems.append(f"{slug}: affiliate URL missing approved tag")

        if row.get("approved_by_chris") is not True:
            problems.append(f"{slug}: approved_by_chris must be true")

        if row.get("live_enabled") is not False:
            problems.append(f"{slug}: live_enabled must remain false before page gate")

        for locked in ["product_swap_allowed", "git_push_allowed", "publish_allowed"]:
            if row.get(locked) is not False:
                problems.append(f"{slug}: {locked} must be false")

    print("RESULT:")

    if problems:
        print("GENERATED REGISTRY INTAKE STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("GENERATED REGISTRY INTAKE STATE: PASS")
    print(f"validated_links: {len(generated.get('links', []))}")
    print("next_required_gate: inject_links_into_pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

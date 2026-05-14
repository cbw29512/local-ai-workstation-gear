"""
Validate Amazon affiliate link registry.

Read-only doctor.
No page edits, commits, pushes, or publishing.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.amazon_links_io import load_json
from webmaster.amazon_links_paths import LINK_REGISTRY
from webmaster.amazon_links_validate import approved_live_links, validate_registry


def main() -> int:
    """Validate registry safety."""
    problems: list[str] = []

    if not LINK_REGISTRY.is_file():
        problems.append(f"missing registry: {LINK_REGISTRY}")
    else:
        data = load_json(LINK_REGISTRY)
        problems.extend(validate_registry(data))

    print("RESULT:")

    if problems:
        print("AMAZON LINK REGISTRY STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    data = load_json(LINK_REGISTRY)
    print("AMAZON LINK REGISTRY STATE: PASS")
    print(f"registry_links: {len(data.get('links', []))}")
    print(f"approved_live_links: {len(approved_live_links(data))}")
    print("next_required_gate: paste_chris_approved_amazon_affiliate_links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

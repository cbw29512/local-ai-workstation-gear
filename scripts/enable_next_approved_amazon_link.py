"""
Enable the next Chris-approved Amazon affiliate link.

Safety:
- Requires approved_by_chris=true.
- Requires live_enabled=true.
- Amazon/amzn.to only.
- No commits or pushes.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.amazon_links_io import load_json
from webmaster.approved_link_intake import INTAKE, upsert_registry, validate_intake


def main() -> int:
    """Enable one approved Amazon link."""
    try:
        row = load_json(INTAKE)
        problems = validate_intake(row)

        if problems:
            print("RESULT: ERROR")
            for problem in problems:
                print(f"- {problem}")
            return 1

        target = upsert_registry(row)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"enabled_slug: {target['slug']}")
    print(f"enabled_asin: {target['asin']}")
    print("next_required_gate: render_approved_amazon_links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

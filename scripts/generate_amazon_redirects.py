"""
Generate approved Amazon redirect pages.

Safety:
- Uses only approved_by_chris + live_enabled links.
- No fake links.
- No commits or pushes.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.amazon_redirects import generate_redirects


def main() -> int:
    """Generate redirect pages."""
    try:
        count = generate_redirects()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"redirect_pages_created: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

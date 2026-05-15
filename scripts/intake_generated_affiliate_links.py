"""
Intake generated Amazon affiliate URLs into the approved link registry.

State:
- Reads generated affiliate links from approved queue.
- Upserts them into the existing Amazon link registry.
- Keeps live publishing disabled.

Safety:
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.generated_link_intake_build import upsert_links
from webmaster.generated_link_intake_io import load_json, setup_logging, write_json
from webmaster.generated_link_intake_paths import BACKUP, GENERATED, REGISTRY


def main() -> int:
    """Run generated link intake."""
    setup_logging()

    try:
        generated = load_json(GENERATED)
        registry = load_json(REGISTRY)

        if generated.get("status") != "generated_affiliate_links_ready":
            raise ValueError("generated links file is not ready")

        shutil.copyfile(REGISTRY, BACKUP)
        changed = upsert_links(registry, generated)
        write_json(REGISTRY, registry)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"registry_updated_links: {changed}")
    print(f"backup: {BACKUP}")
    print("next_required_gate: inject_links_into_pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

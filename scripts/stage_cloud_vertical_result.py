"""
Stage cloud vertical research result into the active target file.

State:
- Reads active cloud vertical handoff.
- Reads staged result JSON.
- Verifies staged vertical matches handoff.
- Copies staged result into active target file.

Safety:
- No affiliate links.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "data/site_portfolio/cloud_vertical_handoff.json"
STAGED = ROOT / "data/site_portfolio/cloud_vertical_results/staged-home-organization.json"
LOG_FILE = ROOT / "logs/stage_cloud_vertical_result.log"


def setup_logging() -> None:
    """Create stage-result log file."""
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


def validate_stage(handoff: dict[str, Any], staged: dict[str, Any]) -> list[str]:
    """Validate staged result before copying."""
    problems: list[str] = []
    expected_slug = handoff.get("vertical_slug")
    actual_slug = staged.get("vertical_slug")

    if actual_slug != expected_slug:
        problems.append(f"vertical_slug expected {expected_slug!r}, got {actual_slug!r}")

    for locked in [
        "affiliate_links_created",
        "publish_recommended",
        "affiliate_link_changes_allowed",
        "product_swap_allowed",
        "git_commit_allowed",
        "git_push_allowed",
        "publish_allowed",
    ]:
        if staged.get(locked) is not False:
            problems.append(f"{locked} must be false")

    return problems


def main() -> int:
    """Copy staged result into active target file."""
    setup_logging()

    try:
        handoff = load_json(HANDOFF)
        staged = load_json(STAGED)
        problems = validate_stage(handoff, staged)

        if problems:
            print("RESULT: NEEDS REVIEW")
            for problem in problems:
                print(f"- {problem}")
            return 1

        target = Path(str(handoff["target_result_file"]))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(STAGED, target)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"staged_result: {STAGED}")
    print(f"target_result_file: {target}")
    print("next_required_gate: run_cloud_vertical_result_doctor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Validate product review intake files.

State schema:
{
  "status": "pass|needs_review",
  "product_packets": 24,
  "batch_01_prompt_exists": bool,
  "affiliate_link_changes_allowed": false
}

Safety:
- Read-only doctor.
- No product changes.
- No affiliate links.
- No git add, commit, or push.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "data/product_review/cloud_review_intake.json"
INSTRUCTIONS = ROOT / "reports/product_review/cloud_review_instructions.md"
BATCH_01 = ROOT / "reports/product_review/cloud_review_batch_01_prompt.md"
PACKETS = ROOT / "data/product_research"


def load_json(path: Path) -> dict:
    """Load JSON and raise a useful error if parsing fails."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to load {path}: {exc}") from exc


def validate_intake(problems: list[str]) -> None:
    """Validate safety locks in the cloud review intake file."""
    if not INTAKE.is_file():
        problems.append(f"missing intake JSON: {INTAKE}")
        return

    intake = load_json(INTAKE)

    false_keys = [
        "approved_for_live_site",
        "affiliate_link_changes_allowed",
        "product_swap_allowed",
        "git_commit_allowed",
        "git_push_allowed",
    ]

    for key in false_keys:
        if intake.get(key) is not False:
            problems.append(f"{key} must be false")

    if intake.get("next_required_gate") != "paste_cloud_review_results":
        problems.append("next_required_gate must be paste_cloud_review_results")


def validate_files(problems: list[str]) -> None:
    """Validate required prompt files and product packet count."""
    if not INSTRUCTIONS.is_file():
        problems.append(f"missing instructions: {INSTRUCTIONS}")

    if not BATCH_01.is_file():
        problems.append(f"missing batch 01 prompt: {BATCH_01}")

    packet_count = len(list(PACKETS.glob("*.json")))

    if packet_count != 24:
        problems.append(f"expected 24 product packets, found {packet_count}")

    if BATCH_01.is_file():
        text = BATCH_01.read_text(encoding="utf-8")

        required = [
            "Starter Local AI Mini PC",
            "Budget AI Workstation Desktop",
            "Mac Mini Local AI Setup",
            "AI Laptop With 32GB RAM",
            "External SSD for AI Model Storage",
            "NVMe SSD for AI Workstations",
            "affiliate_links_created",
            "publish_recommended",
        ]

        for phrase in required:
            if phrase not in text:
                problems.append(f"batch prompt missing: {phrase}")


def main() -> int:
    """Run product review intake doctor."""
    problems: list[str] = []

    validate_files(problems)
    validate_intake(problems)

    print("RESULT:")

    if problems:
        print("PRODUCT REVIEW INTAKE STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("PRODUCT REVIEW INTAKE STATE: PASS")
    print("product_packets: 24")
    print(f"batch_01_prompt: {BATCH_01}")
    print("next_required_gate: paste_cloud_review_results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

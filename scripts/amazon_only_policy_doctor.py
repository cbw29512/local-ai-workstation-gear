"""
Validate Amazon-only monetization policy.

Read-only doctor.
No affiliate links, product swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/product_review/amazon_only_policy.json"
BATCH_PROMPT = ROOT / "reports/product_review/cloud_review_batch_01_prompt.md"
LIVE_DOCS = ROOT / "docs"


def main() -> int:
    """Validate Amazon-only policy files and public disclosure direction."""
    problems: list[str] = []

    if not POLICY.is_file():
        problems.append(f"missing policy: {POLICY}")
    else:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))

        expected = {
            "status": "amazon_only_policy_active",
            "monetization_program": "Amazon Associates",
            "required_disclosure": "As an Amazon Associate I earn from qualifying purchases.",
            "affiliate_links_created_by_ai": False,
            "affiliate_link_changes_allowed": False,
            "product_swap_allowed": False,
            "git_commit_allowed": False,
            "git_push_allowed": False,
            "publish_allowed": False,
            "next_required_gate": "amazon_only_product_research",
        }

        for key, value in expected.items():
            if policy.get(key) != value:
                problems.append(f"{key} expected {value!r}, got {policy.get(key)!r}")

    if not BATCH_PROMPT.is_file():
        problems.append(f"missing batch prompt: {BATCH_PROMPT}")
    else:
        prompt = BATCH_PROMPT.read_text(encoding="utf-8")

        required_phrases = [
            "Amazon Associates only",
            "Every candidate must be from Amazon",
            "Amazon product URL or ASIN",
            "Do not use Walmart",
            "Do not use Walmart, Best Buy, Newegg, Apple, Micro Center",
            "As an Amazon Associate I earn from qualifying purchases.",
            "amazon_only_product_research_completed",
            "affiliate_links_created",
            "publish_recommended",
        ]

        for phrase in required_phrases:
            if phrase not in prompt:
                problems.append(f"batch prompt missing phrase: {phrase}")

    public_html = list(LIVE_DOCS.rglob("*.html")) if LIVE_DOCS.is_dir() else []
    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in public_html
    )

    # Warning-level now, but make it visible before affiliate links go live.
    if "As an Amazon Associate I earn from qualifying purchases." not in public_text:
        problems.append("public docs missing required Amazon Associate disclosure")

    print("RESULT:")

    if problems:
        print("AMAZON-ONLY POLICY STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("AMAZON-ONLY POLICY STATE: PASS")
    print("next_required_gate: amazon_only_product_research")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

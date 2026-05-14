"""
Build active cloud vertical prompt.

State:
- Combines active handoff and source packet.
- Produces one file to send to large/cloud AI.

Safety:
- Prompt only.
- No affiliate links.
- No product swaps.
- No publishing.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "data/site_portfolio/cloud_vertical_handoff.md"
PACKET = ROOT / "data/site_portfolio/cloud_vertical_packets/home-organization.md"
OUT = ROOT / "data/site_portfolio/cloud_vertical_active_prompts/home-organization-active-prompt.md"


def read_text(path: Path) -> str:
    """Read text with clear failure context."""
    if not path.is_file():
        raise FileNotFoundError(f"missing file: {path}")

    return path.read_text(encoding="utf-8")


def main() -> int:
    """Build combined cloud prompt."""
    try:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        content = (
            "# Active Cloud AI Request\n\n"
            "Use this full prompt to return the JSON result only.\n\n"
            "Do not create affiliate links. Do not publish. Do not invent prices, ratings, reviews, or discounts.\n\n"
            "---\n\n"
            + read_text(HANDOFF)
            + "\n\n---\n\n"
            + read_text(PACKET)
        )
        OUT.write_text(content, encoding="utf-8")
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"active_prompt: {OUT}")
    print("next_required_gate: cloud_ai_returns_24_home_organization_products")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

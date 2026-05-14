"""
Render cloud clarification packet for proposed Amazon candidate.
"""

from __future__ import annotations

from typing import Any


def render_cloud_packet(proposal: dict[str, Any]) -> str:
    """Render cloud AI clarification packet."""
    candidates = proposal.get("recommended_candidates", [])

    rows = []

    for candidate in candidates:
        rows.append(
            f"""
## Candidate: {candidate.get('product_name', '')}

- Brand: {candidate.get('brand', '')}
- ASIN: {candidate.get('asin', '')}
- Amazon URL: {candidate.get('amazon_url', '')}
- Confidence: {candidate.get('confidence', '')}

### Why it fits

{candidate.get('why_it_fits', '')}

### Specs to verify

{chr(10).join('- ' + spec for spec in candidate.get('important_specs_to_verify', []))}

### Risk notes

{chr(10).join('- ' + risk for risk in candidate.get('risk_notes', []))}
"""
        )

    return f"""# Cloud AI Candidate Clarification Packet

Site: Local AI Workstation Gear

Proposed slot: {proposal.get('slot')}
Slug: {proposal.get('slug')}
Title: {proposal.get('title')}
Category: {proposal.get('category')}

## Task For Large/Cloud AI

Clarify and verify whether the proposed Amazon product candidate should be approved for this slot.

## Hard Rules

- Amazon-only.
- Candidate must have a real Amazon URL and ASIN.
- Do not invent prices.
- Do not invent ratings.
- Do not invent reviews.
- Do not invent discounts.
- Do not create affiliate links.
- Check fit, compatibility, risk, and page angle.
- Return a final recommendation: approve, hold, or replace candidate.
- Chris must approve before any live product or affiliate link change.

## Local AI Proposed Candidates

{chr(10).join(rows)}

## Required Output

Return:

- final_decision: approve|hold|replace
- best_candidate_product_name
- best_candidate_asin
- reasons
- risk_notes
- page_angle
- Chris approval checklist
"""

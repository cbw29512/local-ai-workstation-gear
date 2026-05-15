# Large AI Manual Handoff

Status: `large_ai_request_ready`

Provider mode: `manual_chatgpt`

Task type: `cloud_vertical_product_research`

Reason:
Home organization vertical needs 24 Amazon-only products.

Target response file:
`/Users/chris/Code/local-ai-workstation-gear/data/site_portfolio/cloud_vertical_results/staged-home-organization.json`

API call allowed: `False`

Manual ChatGPT required: `True`

## Instructions

Paste the prompt below into ChatGPT / Large AI.

Return JSON only. No commentary.

---

You are doing product research for an Amazon-only affiliate site.

Return ONE raw JSON object only.

Do not include markdown.
Do not include code fences.
Do not include commentary.
Do not explain your reasoning outside the JSON.
The first character of your response must be {
The last character of your response must be }

Vertical: home-organization

Site angle:
Simple products that make rooms easier to organize and navigate.

Target result file:
data/site_portfolio/cloud_vertical_results/home-organization.json

Hard rules:
- Return exactly 24 product items.
- Every product must be from Amazon.
- Every item must include an amazon_url.
- Prefer direct Amazon product URLs, not search pages or category pages.
- Include ASIN when you can identify it.
- If ASIN is uncertain, use an empty string and add a risk note.
- Do not create affiliate links.
- Do not invent prices.
- Do not invent ratings.
- Do not invent review counts.
- Do not invent discounts.
- Do not include medical, legal, financial, safety, or guaranteed-result claims.
- Do not recommend blocked/regulated categories.
- Favor useful, item-first pages with simple descriptions.
- Chris approval is required before any product goes live.
- publish_recommended must be false.
- affiliate_links_created must be false.
- ready_for_chris_review should be true only if all 24 items follow these rules.

Preferred item angles:
- entryway drop zone
- closet organization
- cord and cable cleanup
- under-sink storage
- drawer organization
- pantry organization
- laundry room organization
- bathroom counter organization
- small-space storage
- garage shelf organization
- toy/kids room cleanup
- bedroom storage
- office cable cleanup
- cleaning supply storage

Required JSON shape:

{
  "vertical_slug": "home-organization",
  "status": "cloud_vertical_research_completed",
  "recommended_site_name": "",
  "definition_of_done": [
    "24 item-first Amazon product pages",
    "One funnel/controller index page",
    "Amazon-only product URLs/ASINs",
    "FTC/Amazon disclosure",
    "No prices/ratings/reviews unless verified"
  ],
  "items": [
    {
      "slot": 1,
      "page_slug": "",
      "page_title": "",
      "product_name": "",
      "brand": "",
      "asin": "",
      "amazon_url": "",
      "why_it_fits": "",
      "item_angle": "",
      "important_specs_to_verify": [],
      "risk_notes": [],
      "confidence": "low|medium|high"
    }
  ],
  "global_risk_notes": [],
  "ready_for_chris_review": true,
  "affiliate_links_created": false,
  "publish_recommended": false,
  "affiliate_link_changes_allowed": false,
  "product_swap_allowed": false,
  "git_commit_allowed": false,
  "git_push_allowed": false,
  "publish_allowed": false,
  "next_required_gate": "chris_vertical_site_approval"
}

Output requirements:
- The items array must contain exactly 24 objects.
- slot values must be 1 through 24.
- page_slug values must be lowercase, URL-safe, and unique.
- page_title values should sound useful and item-first.
- why_it_fits should be concise and practical.
- risk_notes should mention verification concerns, compatibility, sizing, installation, durability, or claim limits when relevant.
- confidence must be only low, medium, or high.


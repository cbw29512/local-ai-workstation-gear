# Active Cloud AI Request

Use this full prompt to return the JSON result only.

Do not create affiliate links. Do not publish. Do not invent prices, ratings, reviews, or discounts.

---

# Active Cloud Vertical Research Handoff

Status: `cloud_vertical_handoff_ready`

Vertical: `home-organization`

Site angle:
Simple products that make rooms easier to organize and navigate.

Source packet:
`/Users/chris/Code/local-ai-workstation-gear/data/site_portfolio/cloud_vertical_packets/home-organization.md`

Target result file:
`/Users/chris/Code/local-ai-workstation-gear/data/site_portfolio/cloud_vertical_results/home-organization.json`

Required:
- Exactly `24` Amazon-only products.
- Status must be `cloud_vertical_research_completed`.
- Do not create affiliate links.
- Do not invent prices, ratings, reviews, or discounts.
- Chris approval is required before site creation or publishing.

Safety locks:
- Affiliate link changes allowed: `False`
- Product swap allowed: `False`
- Git commit allowed: `False`
- Git push allowed: `False`
- Publish allowed: `False`


---

# Cloud Vertical Product Research Packet

Vertical: home-organization

Site angle:
Simple products that make rooms easier to organize and navigate.

## Example Item Angles

- entryway drop zone
- closet organization
- cord and cable cleanup
- under-sink storage

## Task For Large/Cloud AI

Find 24 Amazon-only product candidates for this vertical.

## Hard Rules

- Amazon-only.
- Each candidate must include an Amazon URL.
- ASIN is required when available.
- Do not create affiliate links.
- Do not invent prices.
- Do not invent ratings.
- Do not invent reviews.
- Do not invent discounts.
- Do not recommend blocked categories.
- Avoid medical, legal, financial, or safety claims.
- Favor useful, item-first pages with clear descriptions.
- Chris approval is required before any product goes live.

## Required Output Shape

Return JSON with:
- vertical_slug
- status: cloud_vertical_research_completed
- recommended_site_name
- definition_of_done
- items: 24 rows
- global_risk_notes
- ready_for_chris_review
- affiliate_links_created: false
- publish_recommended: false

Each item row must include:
- slot
- page_slug
- page_title
- product_name
- brand
- asin
- amazon_url
- why_it_fits
- item_angle
- important_specs_to_verify
- risk_notes
- confidence

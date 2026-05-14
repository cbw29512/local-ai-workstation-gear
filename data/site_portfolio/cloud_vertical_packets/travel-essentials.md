# Cloud Vertical Product Research Packet

Vertical: travel-essentials

Site angle:
Small travel products that make packing and trips easier.

## Example Item Angles

- packing cubes
- toiletry bags
- carry-on organization
- travel chargers

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

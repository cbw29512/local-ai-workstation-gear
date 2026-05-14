# Cloud Vertical Product Research Packet

Vertical: pet-care

Site angle:
Practical pet products for cleaner homes and easier routines.

## Example Item Angles

- dog walking gear
- cat litter cleanup
- pet hair control
- pet travel accessories

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

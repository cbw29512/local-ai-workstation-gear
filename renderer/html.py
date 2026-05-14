"""
HTML rendering helpers.

Public rule:
- index.html is the funnel/controller.
- sites/<slug>/index.html are item-first visitor pages.
"""

from __future__ import annotations

import html
from typing import Any


def esc(value: Any) -> str:
    """Escape text before writing HTML."""
    return html.escape(str(value), quote=True)


def item_card(item: dict[str, Any]) -> str:
    """Render one homepage item card."""
    return f"""
    <article class="card">
      <p class="eyebrow">{esc(item["category"])}</p>
      <h2>{esc(item["title"])}</h2>
      <p>{esc(item["best_for"])}</p>
      <a class="button" href="./sites/{esc(item["slug"])}/">View item guide</a>
    </article>
    """


def render_index(inventory: dict[str, Any]) -> str:
    """Render the funnel/controller homepage."""
    cards = "\n".join(item_card(item) for item in inventory["items"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{esc(inventory["brand"])}</title>
  <meta name="description" content="Simple local AI workstation gear picks organized by use case.">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="./styles.css">
</head>
<body>
  <header class="hero">
    <p class="eyebrow">Beginner-friendly local AI gear</p>
    <h1>{esc(inventory["brand"])}</h1>
    <p>Choose the part of your setup you are working on. Each page is short, practical, and item-first.</p>
  </header>
  <nav class="quick-nav">
    <a href="#items">Items</a>
    <a href="#disclosure">Disclosure</a>
  </nav>
  <main id="items" class="grid">
{cards}
  </main>
  <footer id="disclosure">
    <p><strong>Affiliate disclosure:</strong> Some outbound links may be affiliate links after manual review. We do not invent prices, ratings, or discounts.</p>
  </footer>
</body>
</html>
"""


def render_item_page(inventory: dict[str, Any], item: dict[str, Any]) -> str:
    """Render one visitor-facing item page."""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{esc(item["title"])} | {esc(inventory["brand"])}</title>
  <meta name="description" content="{esc(item["title"])}: {esc(item["best_for"])}">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <header class="hero compact">
    <p class="eyebrow">{esc(item["category"])}</p>
    <h1>{esc(item["title"])}</h1>
    <p>{esc(item["best_for"])}</p>
  </header>
  <main class="item-layout">
    <section class="card primary">
      <h2>What to look for</h2>
      <p>Use this page as a quick filter before buying. Focus on compatibility, memory, storage, cooling, and whether the item fits your actual local AI workload.</p>
    </section>
    <section class="card">
      <h2>Best for</h2>
      <p>{esc(item["best_for"])}</p>
    </section>
    <section class="card">
      <h2>Status</h2>
      <p>This slot is marked <strong>{esc(item["status"])}</strong>. Add approved product links only after manual review.</p>
    </section>
    <section class="card">
      <h2>Navigation</h2>
      <p><a class="button" href="../../">Back to all local AI gear</a></p>
    </section>
  </main>
  <footer>
    <p><strong>Affiliate disclosure:</strong> Some outbound links may be affiliate links after manual review. No prices, ratings, or discounts are shown unless verified.</p>
  </footer>
</body>
</html>
"""

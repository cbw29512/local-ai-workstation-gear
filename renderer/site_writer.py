"""
Public page writer.

This writes local static files only.
"""

from __future__ import annotations

import logging
import shutil

from renderer.html import render_index, render_item_page
from renderer.io import write_text
from renderer.paths import ROOT


def remove_legacy_public_surfaces() -> None:
    """Remove old Home Depot public surfaces before rendering clean pages."""
    try:
        for relative in ["pages", "hubs"]:
            target = ROOT / relative
            if target.exists():
                shutil.rmtree(target)

        sites_dir = ROOT / "sites"
        if sites_dir.exists():
            shutil.rmtree(sites_dir)

        sites_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        logging.exception("Failed to remove legacy public surfaces: %s", exc)
        raise


def write_pages(inventory: dict) -> None:
    """Write funnel and item pages from source-of-truth inventory."""
    try:
        write_text(ROOT / "index.html", render_index(inventory))

        for item in inventory["items"]:
            page_dir = ROOT / "sites" / item["slug"]
            write_text(page_dir / "index.html", render_item_page(inventory, item))
    except Exception as exc:
        logging.exception("Failed to write public pages: %s", exc)
        raise

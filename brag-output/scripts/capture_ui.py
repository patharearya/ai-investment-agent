"""Capture real components of the running web app for the video.

Start the app first:  python -m uvicorn frontend.app:app --port 8765
Then:                 python brag-output/scripts/capture_ui.py brag-output/work/ui

Every image is the app's own markup and CSS, rendered by the app and cropped to
one element at 2x, so the video shows the real thing rather than a re-creation.
Only recorded gallery runs are opened: no model call and no quota is spent.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
base = "http://127.0.0.1:8765/"


def settle(pg, h):
    pg.goto(base + h)
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(1200)


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
    settle(pg, "")
    pg.locator(".banner h1").screenshot(path=str(out / "title.png"))
    pg.locator(".stats").screenshot(path=str(out / "stats.png"))
    for i, li in enumerate(pg.locator("ol.steps li").all(), 1):
        li.screenshot(path=str(out / f"step{i}.png"))

    settle(pg, "#gallery/technology")
    pg.locator("#gallery-result section.panel").first.screenshot(path=str(out / "card.png"))

    settle(pg, "#gallery/nothing-recommended")
    pg.locator("#gallery-result section.nothing").screenshot(path=str(out / "nothing.png"))

    settle(pg, "#gallery")
    pg.locator("#gallery-list").screenshot(path=str(out / "gallery.png"))
    b.close()

"""Render diagrams/src/*.drawio to diagrams/png/*.png, using the diagrams.net viewer in headless Chromium.

    python diagrams/render_diagrams.py [name ...]

No draw.io install needed: the page loads viewer-static.min.js from diagrams.net and the diagram XML
is passed inline. Transparent background, so the PNG sits on light or dark slides. Rendered at 2x.
"""
import html, json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent; SRC, PNG = HERE / "src", HERE / "png"; PNG.mkdir(exist_ok=True)
VIEWER = "https://viewer.diagrams.net/js/viewer-static.min.js"
names = sys.argv[1:] or sorted(p.stem for p in SRC.glob("*.drawio"))

def model_xml(drawio_text):
    return re.search(r"<mxGraphModel.*?</mxGraphModel>", drawio_text, re.S).group(0)

def page_for(xml):
    cfg = json.dumps({"highlight": "none", "nav": False, "resize": True, "toolbar": "", "xml": xml})
    return (f"<!doctype html><html><head><meta charset=\"utf-8\"></head><body style=\"margin:0;background:transparent\">"
            f"<div class=\"mxgraph\" data-mxgraph='{html.escape(cfg, quote=True)}'></div>"
            f"<script src=\"{VIEWER}\"></script></body></html>")

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for name in names:
        tmp = PNG / f"_{name}.html"; tmp.write_text(page_for(model_xml((SRC / f"{name}.drawio").read_text(encoding="utf-8"))), encoding="utf-8")
        done = False
        for dsf in (2, 1):                                   # the viewer occasionally refuses a 2x context; fall back to 1x
            ctx = b.new_context(viewport={"width": 1800, "height": 1100}, device_scale_factor=dsf); pg = ctx.new_page()
            pg.goto(tmp.resolve().as_uri())
            for _ in range(40):
                if pg.evaluate("document.querySelectorAll('.mxgraph svg').length") > 0: break
                pg.wait_for_timeout(250)
            if pg.evaluate("document.querySelectorAll('.mxgraph svg').length") > 0:
                pg.wait_for_timeout(1200)
                pg.query_selector(".mxgraph svg").screenshot(path=str(PNG / f"{name}.png"), omit_background=True)
                print(f"rendered {name} at {dsf}x", flush=True); done = True
            ctx.close()
            if done: break
        tmp.unlink()
        if not done: print(f"FAILED {name}", flush=True)
    b.close()

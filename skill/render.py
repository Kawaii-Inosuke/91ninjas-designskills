"""Render an infographic spec to HTML + PNG with the client's brand tokens.

  render.py build --spec spec.json [--force]   next version vN in output/<client>/<slug>/
  render.py icons <word> [<word>...]           search icon names (Tabler, restyled per brand)

Spec (written by Claude from the outline):
  {"client": "fcc", "title": "...", "layout": "vertical_list/number",
   "items":   [{"heading": "...", "body": "...", "icon": "chart-bar"}],         # list / timeline / cards
   "columns": [{"title": "...", "flow": ["A", "B"], "items": ["..."]}],         # comparison / 3-col
   "table":   {"header": ["Basis", "A", "B"], "rows": [["Scope", "...", "..."]]},
   "takeaway": "optional one-line summary",
   "html": "<custom body markup>",                                           # layout "custom"
   "css": "per-infographic overrides (critic fixes); never edit brand.css for one piece"}
Prints JSON: files, auto_checks (machine-found problems), revisions_left.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import jinja2
from markupsafe import Markup
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand  # noqa: E402
from registry import CFG, ROOT  # noqa: E402

ICONS = ROOT / "skill/icons/tabler"
ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(ROOT / CFG["paths"]["templates"]),
                         autoescape=True, trim_blocks=True, lstrip_blocks=True)


def icon(name, size, stroke=1.5):
    """Inline any SVG icon in brand style: currentColor strokes, one stroke weight, given size.
    Looks in the brand's assets/icons first (designer-supplied), then Tabler."""
    paths = [p for p in (ENV.globals["brand_dir"] / "assets/icons" / f"{name}.svg", ICONS / f"{name}.svg") if p.exists()]
    if not paths:
        return ""
    svg = paths[0].read_text()
    svg = re.sub(r'\s(width|height|class|stroke-width)="[^"]*"', "", svg)
    svg = re.sub(r'\sfill="(?!none)[^"]*"', ' fill="currentColor"', svg)
    svg = re.sub(r'\sstroke="(?!none)[^"]*"', ' stroke="currentColor"', svg)
    return svg.replace("<svg", f'<svg width="{size}" height="{size}" stroke-width="{stroke}" aria-hidden="true"', 1)


def font_faces(brand_dir):
    faces = []
    for f in sorted((brand_dir / "assets/fonts").glob("*-*.woff2")):
        family, weight = f.stem.rsplit("-", 1)
        faces.append(f"@font-face {{ font-family: '{family}'; font-weight: {weight}; "
                     f"src: url('{f.as_uri()}') format('woff2'); }}")
    return "\n".join(faces)


def build_html(spec, tokens):
    ig = tokens.get("infographic", {})
    ic = ig.get("icon", {})
    ENV.globals.update(brand_dir=tokens["dir"],
                       icon=lambda n, s: Markup(icon(n, round(s * ic.get("scale", 0.6)),
                                                                              ic.get("stroke", 1.5))))
    family, _, variant = spec["layout"].partition("/")
    css = tokens["dir"] / "assets/brand.css"
    return ENV.get_template(f"{family}.html.j2").render(
        spec=spec, variant=variant, items=spec.get("items", []), columns=spec.get("columns", []),
        table=spec.get("table"), width=ig.get("canvas", CFG["render"]["default_canvas"])["width"],
        content_max=ig.get("content_max_width", 1500), css_vars=Markup(brand.css_vars(tokens)),
        font_faces=Markup(font_faces(tokens["dir"])), brand_css=Markup(css.read_text() if css.exists() else ""))


AUTO_CHECKS = """([width, maxH, fonts, palette]) => {
  const out = [], hex = c => { const m = c.match(/\\d+(\\.\\d+)?/g); if (!m || (m[3] !== undefined && +m[3] === 0)) return null;
    return '#' + m.slice(0, 3).map(v => (+v).toString(16).padStart(2, '0')).join('').toUpperCase(); };
  const canvas = document.querySelector('#canvas'), H = canvas.scrollHeight;
  if (canvas.scrollWidth > width) out.push(`canvas wider than ${width}px (${canvas.scrollWidth})`);
  if (H > maxH) out.push(`canvas taller than ${maxH}px (${H})`);
  for (const f of fonts) if (!document.fonts.check(`16px "${f}"`)) out.push(`font not loaded: ${f}`);
  const off = new Set(), small = new Set();
  for (const el of document.querySelectorAll('#canvas *')) {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (hasText) {
      if (!fonts.some(f => s.fontFamily.includes(f))) out.push(`wrong font "${s.fontFamily}" on: ${el.textContent.trim().slice(0, 40)}`);
      if (parseFloat(s.fontSize) < 20) small.add(`${s.fontSize} "${el.textContent.trim().slice(0, 30)}"`);
      if (el.scrollWidth > el.clientWidth + 1 && s.overflow !== 'visible') out.push(`text clipped: ${el.textContent.trim().slice(0, 40)}`);
    }
    if (r.right > width + 1 || r.left < -1) out.push(`outside canvas: <${el.tagName.toLowerCase()} class="${el.className.baseVal ?? el.className}">`);
    const box = el.closest('.card, .cell, .pill, .takeaway');
    if (box && box !== el && hasText) { const b = box.getBoundingClientRect();
      if (r.right > b.right + 1 || r.bottom > b.bottom + 1) out.push(`text overflows its box: ${el.textContent.trim().slice(0, 40)}`); }
    const shape = el instanceof SVGGeometryElement;
    for (const p of shape ? ['fill', 'stroke'] : ['color', 'backgroundColor', 'borderTopColor']) {
      if (p === 'borderTopColor' && parseFloat(s.borderTopWidth) === 0) continue;
      if (p === 'color' && !hasText) continue;
      if (shape && (s[p] === 'none' || el.getAttribute(p) === 'none')) continue;
      const h = hex(s[p] || ''); if (h && !palette.includes(h)) off.add(`${h} (${p})`);
    }
  }
  for (const svg of document.querySelectorAll('#canvas .marker svg, #canvas .hex-inner svg')) {
    const r = svg.getBoundingClientRect(); if (r.width < 4 || r.height < 4) out.push('icon not visible (zero size)'); }
  if (off.size) out.push('off-palette colours: ' + [...off].join(', '));
  if (small.size) out.push('text under 20px: ' + [...small].slice(0, 5).join('; '));
  return [...new Set(out)];
}"""


def shoot(html_path, png_path, tokens):
    from playwright.sync_api import sync_playwright
    ig = tokens.get("infographic", {})
    width = ig.get("canvas", CFG["render"]["default_canvas"])["width"]
    fonts = sorted({t["fontFamily"] for t in tokens.get("typography", {}).values()})
    palette = sorted(set(brand.palette(tokens).values()) | {"#FFFFFF"})
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_context(viewport={"width": width, "height": 400},
                             device_scale_factor=ig.get("device_scale_factor", 1)).new_page()
        page.goto(html_path.as_uri())
        page.evaluate("document.fonts.ready")
        checks = page.evaluate(AUTO_CHECKS, [width, CFG["render"]["max_height"], fonts, palette])
        page.locator("#canvas").screenshot(path=str(png_path))
        b.close()
    return checks


def build(spec, force=False):
    tokens = brand.load(spec["client"])
    slug = spec.get("slug") or re.sub(r"[^a-z0-9]+", "-", spec["title"].lower()).strip("-")[:60]
    out = ROOT / CFG["paths"]["output"] / spec["client"] / slug
    out.mkdir(parents=True, exist_ok=True)
    n = len(list(out.glob("v*.html"))) + 1
    max_v = CFG["critic"]["max_revisions"] + 1
    if n > max_v and not force:
        return {"error": f"revision limit reached ({max_v - 1} revisions). Show the designer the best version."}
    html, png, preview = out / f"v{n}.html", out / f"v{n}.png", out / f"v{n}_preview.png"
    html.write_text(build_html(spec, tokens))
    (out / f"v{n}.json").write_text(json.dumps(spec, indent=1))
    checks = shoot(html, png, tokens)
    im = Image.open(png)
    w = CFG["critic"]["preview_width"]
    im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(preview)
    return {"version": n, "html": str(html), "png": str(png), "preview": str(preview), "size": list(im.size),
            "brand_version": tokens.get("brand_version"), "auto_checks": checks,
            "critic_rules": [str(p) for p in tokens["critic_rules"]], "revisions_left": max_v - n}


def main():
    p = argparse.ArgumentParser(description="Render infographic")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("build")
    s.add_argument("--spec", required=True)
    s.add_argument("--force", action="store_true")
    sub.add_parser("icons").add_argument("words", nargs="+")
    a = p.parse_args()
    if a.cmd == "icons":
        names = sorted(f.stem for f in ICONS.glob("*.svg"))
        out = {w: [n for n in names if w in n][:15] for w in a.words}
    else:
        out = build(json.loads(Path(a.spec).read_text()), a.force)
    print(json.dumps(out, indent=1))
    sys.exit(1 if "error" in out else 0)


if __name__ == "__main__":
    main()

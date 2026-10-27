"""Backfill old infographics into the registry, cheaply.

  analyze.py prepare --client C [--src brands/C/past]
      Renders every SVG/PNG/JPEG to PNG, computes phash + palette usage locally (no tokens),
      and builds contact sheets (6 thumbnails each) so Claude reads ~6 infographics per image.
      Writes output/backfill/C/metrics.json and sheet*.png.

  (Claude views the sheets and writes output/backfill/C/tags.json:
   [{"n": 0, "topic": "...", "angle": "...", "key_points": ["..."], "layout_type": "family/variant"}])

  analyze.py finish --client C [--status approved|old_brand]
      Merges tags + metrics and inserts via registry.backfill.
"""
import argparse
import json
import sys
from pathlib import Path

import imagehash
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand  # noqa: E402
import registry  # noqa: E402

THUMB = 640


def render_svgs(svgs, out):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1920, "height": 800})
        for src, dst in zip(svgs, out):
            page.goto(src.resolve().as_uri())
            page.locator("svg").first.screenshot(path=str(dst))
        b.close()


def palette_usage(img, pal):
    """Share of non-white pixels nearest each brand colour; pixels far from all of them count as off_brand."""
    a = np.asarray(img.convert("RGB").resize((480, int(480 * img.height / img.width))), dtype=int).reshape(-1, 3)
    a = a[(a < 245).any(1)]
    if not len(a):
        return {}
    names = list(pal)
    ref = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in pal.values()])
    dist = np.abs(a[:, None, :] - ref[None]).sum(2)
    near, best = dist.argmin(1), dist.min(1)
    usage = {names[i]: round(float(((near == i) & (best < 60)).mean()), 3) for i in range(len(names))}
    usage["off_brand"] = round(float((best >= 60).mean()), 3)
    return {k: v for k, v in usage.items() if v}


def contact_sheets(pngs, out_dir):
    sheets = []
    for s in range(0, len(pngs), 6):
        thumbs = []
        for p in pngs[s:s + 6]:
            im = Image.open(p).convert("RGB")
            im.thumbnail((THUMB, THUMB * 3))
            thumbs.append(im)
        row_h = max(t.height for t in thumbs) + 30
        sheet = Image.new("RGB", (THUMB * 3, row_h * ((len(thumbs) + 2) // 3)), "#999")
        draw = ImageDraw.Draw(sheet)
        for j, t in enumerate(thumbs):
            x, y = (j % 3) * THUMB, (j // 3) * row_h
            sheet.paste(t, (x, y + 30))
            draw.text((x + 6, y + 8), f"#{s + j}", fill="black")
        path = out_dir / f"sheet{s // 6}.png"
        sheet.save(path)
        sheets.append(str(path))
    return sheets


def prepare(client, src):
    out = registry.ROOT / "output/backfill" / client
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(f for f in src.iterdir() if f.suffix.lower() in (".svg", ".png", ".jpg", ".jpeg"))
    pngs = [out / f"{i:03d}.png" for i in range(len(files))]
    svg_idx = [i for i, f in enumerate(files) if f.suffix.lower() == ".svg"]
    render_svgs([files[i] for i in svg_idx], [pngs[i] for i in svg_idx])
    for i, f in enumerate(files):
        if i not in svg_idx:
            Image.open(f).convert("RGB").save(pngs[i])
    pal = brand.palette(brand.load(client))
    metrics = []
    for i, (f, p) in enumerate(zip(files, pngs)):
        im = Image.open(p)
        metrics.append({"n": i, "source": f.name, "hint": f.stem.removeprefix("Infographic - ").strip(),
                        "size": list(im.size), "phash": str(imagehash.phash(im)),
                        "palette_usage": palette_usage(im, pal)})
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    return {"count": len(files), "sheets": contact_sheets(pngs, out), "metrics": str(out / "metrics.json"),
            "hints": [{"n": m["n"], "hint": m["hint"]} for m in metrics],
            "next": f"view sheets, write {out / 'tags.json'}, then run: analyze.py finish --client {client}"}


def finish(client, status):
    out = registry.ROOT / "output/backfill" / client
    metrics = {m["n"]: m for m in json.loads((out / "metrics.json").read_text())}
    tags = json.loads((out / "tags.json").read_text())
    version = brand.load(client).get("brand_version")
    rows = [{**t, "source": metrics[t["n"]]["source"], "phash": metrics[t["n"]]["phash"],
             "brand_version": t.get("brand_version", version)} for t in tags]
    with registry.connect() as conn:
        return registry.backfill(conn, client, rows, status)


def main():
    p = argparse.ArgumentParser(description="Backfill old infographics")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prepare")
    s.add_argument("--client", required=True)
    s.add_argument("--src")
    s = sub.add_parser("finish")
    s.add_argument("--client", required=True)
    s.add_argument("--status", default="approved", choices=["approved", "old_brand"])
    a = p.parse_args()
    if a.cmd == "prepare":
        out = prepare(a.client, Path(a.src) if a.src else registry.ROOT / "brands" / a.client / "past")
    else:
        out = finish(a.client, a.status)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

---
name: infographic
description: Turn a content part (text or image) into an on-brand client infographic PNG. Loads the client's DESIGN.md brand pack, blocks repeats via the shared Supabase registry, renders HTML to PNG with Playwright, runs a critic loop, and logs only after designer approval. Use when a designer asks to make an infographic for a client (e.g. "make an FCC infographic from this").
argument-hint: "<client> <content text or image path>"
---

# Infographic skill

Run every command from the repo root with the project Python: `.venv/bin/python` on macOS/Linux/web,
`.venv\Scripts\python` on Windows (written as `.venv/bin/python` below). All scripts print JSON.
If `.venv` is missing, tell the designer to run `bash scripts/setup.sh` (Mac/web) or `scripts\setup.ps1` (Windows) first.
Two hard gates: **outline approval** (step 6) and **final approval** (step 9). Nothing is logged without the second.
Never make an infographic that already exists. Keep token use low: read JSON, view only the 960px preview.

## 1. Sync
If the repo has a git remote: `git pull --ff-only` (brand packs live in `brands/`). If it fails or there is no remote, say so in one line and continue.

## 2. Load the brand
Client folder = lowercase short name (`fcc`). Read, in this order:
- `brands/<client>/DESIGN.md` (front matter = tokens, `brand_version`, `infographic` block: canvas, layouts, layout_window, icon rules)
- `brands/<client>/critic_rules.md`, then `skill/critic_rules.md` (brand wins on conflict)
If the folder does not exist: stop and offer to create it from `brands/_template/` (see "New client").

## 3. Extract
From the content part (text, or an image you view once):
- **topic**: one line, acronyms written out with the short form, e.g. "Minimum order value (MOV) thresholds".
- **angle**: what this piece says about the topic (steps, comparison, types, metrics, causes...).
- **key points**: only facts present in the content. Never invent numbers, names or claims.
- **shape** of the content -> layout family from the brand's `layouts` list:
  sequence/steps -> vertical_list, horizontal_timeline, s_curve; two things -> comparison_cards;
  attributes across items -> cell_table; checklist/tips -> card_list; types/parts -> central_spine, three_column_grid;
  term + formula + example -> three_column_grid; tiers/maturity -> custom staircase or pyramid.
Store nothing but topic, angle and key points (no full client documents).

## 4. Check (dedup)
`.venv/bin/python skill/registry.py check --client <c> --topic "<topic>" --angle "<angle>" --window <layout_window>`
- `block` -> stop. Show the matching approved infographic (topic, layout, date). Suggest a genuinely different angle only if the designer asks.
- `warn` -> show the closest match. If it is a pending row, name who reserved it and when.
- Always read the top matches yourself: if one is the same infographic in different words, treat it as `block` even if the score is lower.
- `avoid_layouts`: do not pick a layout family listed there.

## 5. Reserve
`.venv/bin/python skill/registry.py reserve --client <c> --topic "..." --angle "..." --key-points "<one per line>" --layout <family/variant> --brand-version <v>`
Keep the returned `id`. If the designer abandons at any point: `registry.py release --id <id>`.

## 6. Outline -> APPROVAL GATE
Show, compactly: title (fits one line in the header), layout family/variant and one-line reason, each item's
heading + body as it will appear, icons (search with `skill/render.py icons <word>`), optional takeaway.
- Only if the right shape is unclear, ask for direction in one short question (e.g. "staircase, 4-pointer, or timeline?").
- Any shape or change the designer asks for is implemented, even if it is not in the layouts list (use `custom`).
- Wait for approval. Apply edits and re-show only what changed.

## 7. Render
Write the spec to `output/<client>/<slug>/spec.json` (fields documented at the top of `skill/render.py`), then
`.venv/bin/python skill/render.py build --spec output/<client>/<slug>/spec.json`
For `custom` layouts write `html` using brand classes (`.card .pill .h .b .bullets .marker .takeaway`) and CSS variables only.

## 8. Critic loop (max 3 revisions)
Each pass:
1. Fix every item in `auto_checks` (font, palette, overflow, canvas) first; these are machine-verified.
2. View the `preview` PNG once. Score it against the brand critic rules, then the base rules.
3. List only FAILs as `rule | problem | fix`. Revise the spec (`items`, `css` for one-off tweaks; never edit `brand.css` for a single piece) and rebuild.
Stop at 0 FAILs or when `render.py` reports the revision limit; then pick the best version.

## 9. Final -> APPROVAL GATE
Give the designer the full-size PNG path and HTML path, the layout used, and any rule you could not satisfy.
Options: approve, request changes (back to step 7; the revision limit can be lifted with `--force` only if the designer asks), or abandon (release).

## 10. Log
`.venv/bin/python skill/registry.py log --id <id> --png <vN.png> --html <vN.html> --layout <family/variant> --brand-version <v>`
If it reports `visual_duplicates`, show them; use `--force` only if the designer confirms it is different.
Report the logged id in one line.

## New client
1. `cp -r brands/_template brands/<client>`; fill `DESIGN.md` (bump `brand_version` + `updated` on every change) and `critic_rules.md`.
2. Add `assets/brand.css` (copy FCC's as a start), fonts as `assets/fonts/<Family>-<weight>.woff2`, optional `assets/icons/*.svg`.
3. Put old infographics (SVG with text not outlined > PNG > JPEG) in `brands/<client>/past/`, then backfill:
   `skill/analyze.py prepare --client <c>` -> view the contact sheets -> write `output/backfill/<c>/tags.json` -> `skill/analyze.py finish --client <c>`.

## Rebrand
Bump `brand_version`, then mark old work: `update infographics set status='old_brand' where client='<c>' and brand_version <> '<new>'` (admin).
Old-brand rows still block repeated topics but are not used as style reference.

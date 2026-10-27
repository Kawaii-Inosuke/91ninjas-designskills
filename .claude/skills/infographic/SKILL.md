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
- Skill code: if the repo has a git remote, `git pull --ff-only` (the repo is public; no GitHub account needed). If it fails, say so in one line and continue.
- Brand packs: `.venv/bin/python skill/brands_sync.py pull` installs the newest admin-approved pack of every client from Supabase.

## 2. Load the brand
Client folder = lowercase short name (`fcc`). Read, in this order:
- `brands/<client>/DESIGN.md` (front matter = tokens, `brand_version`, `infographic` block: canvas, layouts, layout_window, icon rules)
- `brands/<client>/critic_rules.md`, then `skill/critic_rules.md` (brand wins on conflict)
If the folder does not exist: stop and offer to create it (see "New client").
If `brands_sync.py pull` said the local pack is "not approved yet", warn the designer that work made now uses an unreviewed brand.

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

## 9b. Export
On approval, export the chosen version (default all three; ask only if the designer named formats):
`.venv/bin/python skill/render.py export --html <vN.html> --formats svg,jpeg,pdf`
- **SVG**: live, editable text (Inter + weights) for small fixes in Figma or Illustrator.
- **JPEG**: for channels that need it. **PDF**: vector, for print or review. **PNG** already exists.

## 10. Log
`.venv/bin/python skill/registry.py log --id <id> --png <vN.png> --html <vN.html> --layout <family/variant> --brand-version <v>`
If it reports `visual_duplicates`, show them; use `--force` only if the designer confirms it is different.
Exports sitting next to the PNG (svg, jpg, pdf) are uploaded too. Report the logged id and all file paths in one line each.

## New client (designer; no GitHub needed)
Inputs: the brand guideline (PDF/doc/images) and old infographics.
1. `cp -r brands/_template brands/<client>`. Read the guideline once; fill `DESIGN.md` (tokens, `brand_version: 1.0.0`, `updated`)
   and `critic_rules.md`. Add `assets/brand.css` (start from FCC's, change only tokens/shapes), fonts as
   `assets/fonts/<Family>-<weight>.woff2`, optional `assets/icons/*.svg`, the guideline in `source/`.
2. Put old infographics in `brands/<client>/past/` (SVG with text not outlined > PNG > JPEG).
   `skill/analyze.py prepare --client <c>` -> view the contact sheets -> write `output/backfill/<c>/tags.json`.
3. Measure the old work against the guideline (colours, sizes, radii, layouts). Where they disagree, the approved
   old work wins; list every disagreement for the designer. Render one sample from an old piece's content and compare.
4. Backfill preview: `skill/analyze.py finish --client <c>` shows the rows. **Designer approves**, then rerun with `--yes`.
   Rows are saved as `review`: they warn on repeats but only count as approved once the admin approves the brand.
5. `skill/brands_sync.py submit --client <c>`. Tell the designer: "Submitted for admin review; you can use it now,
   everyone else gets it after approval."

## Admin: review brand packs (BRAND_ADMIN=1)
`skill/brands_sync.py list --status pending` -> `review --client <c> --version <v>` (installs it locally) ->
read DESIGN.md + critic_rules.md, render one sample, show the admin -> on their decision
`approve --client <c> --version <v>` (backfill rows become approved) or `reject ... --note "why"` (backfill rows deleted).
Optionally give the admin git commands to commit `brands/<c>/` for history. Never commit or push yourself.

## Brand update / rebrand
Edit the pack, bump `brand_version` + `updated`, `submit` again; admin approves as above.
For a full rebrand the admin then marks old work: `update infographics set status='old_brand' where client='<c>' and brand_version <> '<new>'`.
Old-brand rows still block repeated topics but are not used as style reference.

# Infographic Skill: project history and decisions

The record of how this skill was built (Oct 27–28, 2026): what was done, what was decided, and why.
Read this before changing the skill, so you build on the decisions instead of redoing them.

---

## 1. What the skill does

A Claude Code skill that turns a **content part (text or image)** plus a **client name** into an on-brand infographic.

1. Pulls the latest brand packs (Supabase) and code (`git pull`).
2. Loads the client's brand pack (`brands/<client>/DESIGN.md` + `critic_rules.md`).
3. Extracts topic, angle and key points from the content.
4. **Checks the shared registry**, so an infographic that already exists is never made again.
5. Reserves the topic, so other designers see it is in progress.
6. Shows an outline and layout. **The designer approves.**
7. Renders HTML to PNG with Playwright; the critic loop fixes problems (max 3 revisions).
8. Shows the result. **The designer approves** or asks for changes.
9. Exports SVG (editable), JPEG and PDF, uploads everything and logs it as approved.

The workflow lives in `.claude/skills/infographic/SKILL.md`. Setup and usage are in `README.md`.

---

## 2. Build timeline

The build followed the original 8-step plan, with an approval gate at every step.

| Step | What was built | Notes |
|---|---|---|
| 1 | Folders `reference/ brands/ skill/ sql/`, `.gitignore` | `.env` and `reference/` are ignored |
| 2 | Cloned 14 inspiration repos into `reference/` (read only) | All cloned; never installed or run |
| 3 | `docs/SUMMARY.md` (what each repo offers), `skill/critic_rules.md` | Animation and component repos parked for v2 |
| 4 | Folder layout + `skill/config.yaml` | Per-brand canvas sizes |
| 5 | `sql/schema.sql`, `skill/registry.py`, `tests/` | Supabase set up; 4 tests pass |
| 6 | `brands/_template/`, FCC brand pack, `skill/analyze.py`, backfill of 20 FCC infographics | Duplicate thresholds calibrated |
| 7 | `skill/render.py`, layout templates, FCC `brand.css`, icons, critic loop | Rebuilt 6 past FCC pieces to verify |
| 8 | `SKILL.md`, end-to-end test (retail media network), logged | Critic caught a real bug in v1 |
| after | README, setup scripts, exports, brand sharing via Supabase, editor fixes | See sections 6–9 |
| Oct 28 | 5-piece FCC test run, icon scale fix for custom layouts, type-checker fixes | See section 9 |

---

## 3. Key decisions (and why)

### Brand rules
- **Each brand has its own critic rules** (`brands/<client>/critic_rules.md`), loaded before the base rules
  (`skill/critic_rules.md`). When they conflict, the brand wins.
  *Why:* every client has different guidelines; generic "anti-AI-look" rules must not override a client's style.
- **Each brand sets its own canvas size** in its `DESIGN.md` (`infographic.canvas`). For FCC: 1920px wide, height fits content.
- **Approved past work beats the written guideline.** FCC_rules.md said 34–36px body text, Semi-Bold headings and `#2872ED`
  as the second blue. The 20 approved FCC files actually use about 30px body, Medium headings, `#4E93F5` (used 159 times)
  and a 20px radius. The rules were rewritten to match, in `brands/fcc/source/FCC_rules.md`.

### Duplicate check (the registry)
- **Model:** `sentence-transformers/all-MiniLM-L6-v2`, pinned in config. It was tested against `bge-small`, which scored
  new topics as high as duplicates, so it was rejected.
- **Thresholds calibrated on the FCC backfill:** block at 0.80 or above, warn at 0.65 or above. The starting values
  (0.85 / 0.75) let most reworded duplicates through.
- **Two fingerprints per row:** topic + angle, and topic only. The check uses the higher score, so a bare topic still matches.
- **Acronyms are written out** in topics, e.g. "Minimum order value (MOV)"; the model does not link MOV with its expansion.
- **Claude also reads the top 3 matches by meaning** every time, which catches rewordings that score low.
- **Pending reservations and `review` rows only warn;** only `approved` and `old_brand` rows block.
- **Visual duplicates:** a perceptual hash (phash) at `log` time; distance of 8 or less counts as a duplicate unless `--force`.

### Layouts
- **Claude picks the layout from the shape of the content** (steps, comparison, attributes, checklist, types…).
- **It asks only for the direction when the shape is unclear** (e.g. "staircase or timeline?").
- **Any shape the designer asks for gets built**, even if it isn't in the list: the `custom` layout lets Claude write
  the body markup using brand classes.
- **Never repeat the previous layout family** (FCC `layout_window: 1`).

### Rendering
- **Templates hold structure only; each brand's look is in `brands/<client>/assets/brand.css`.** A new client needs no new templates.
- **Icons:** about 5,200 Tabler icons (MIT) kept in `skill/icons/`, restyled to the brand colour and stroke, and sized as
  about 0.6× the item they sit in. Icons in `brands/<client>/assets/icons/` are used first.
  Custom layouts must insert icons as `{{ icon('name', <tile px>) }}`, never pasted SVG, so the brand scale applies.
- **Fonts are kept in the brand pack** (`assets/fonts/<Family>-<weight>.woff2`), so every designer's output is identical.
- **Automatic checks** run on every render at no token cost: wrong font, colour outside the palette, text overflow, outside
  the canvas, text under 20px, invisible icons, canvas too tall.
- **Token saving:** the critic views a 960px preview; the backfill reads 6 thumbnails per image (20 infographics cost about 6k tokens).

### Exports
- **SVG with live, editable text** (Inter with the right weights), made by printing to PDF in Chromium and converting the
  page with PyMuPDF. Designers can make small fixes in Figma or Illustrator.
- PNG (the default), JPEG (quality 95) and PDF (vector) are also produced. `log` uploads every export.

### Sharing brands without GitHub
Most designers have no GitHub account, so **brand packs are shared through Supabase**:
- A designer submits a new brand; it is stored as `pending`, and its backfill rows as `review`.
- The admin (`BRAND_ADMIN=1` in `.env`) reviews, then approves or rejects it.
- On approval, every designer's skill downloads it at the start of the next job (`brands_sync.py pull`).
- The repo is **public**, so designers can clone and pull code updates without an account.

### Git
- **Claude never commits or pushes.** The user commits manually.
- Internal planning docs (`01-PRD.md`, `02-TRD.md`, `03-ARCHITECTURE.md`) are git-ignored and kept local.

---

## 4. Architecture

```text
Designer (Claude Code, inside this repo)
   │  "make an FCC infographic from this: …"
   ▼
.claude/skills/infographic/SKILL.md ── workflow + 2 approval gates
   │
   ├─ skill/brands_sync.py ── pull approved brand packs ◄──► Supabase Storage "brands" + table brand_packs
   ├─ skill/brand.py ──────── DESIGN.md → tokens, CSS variables, palette, rule files
   ├─ skill/registry.py ───── check / reserve / release / log / list / backfill / reembed ◄──► Supabase Postgres
   │                                                                                           (pgvector "infographics")
   ├─ skill/render.py ─────── spec → HTML (templates + brand.css) → PNG + auto checks; export svg/jpeg/pdf
   ├─ skill/analyze.py ────── backfill old work (contact sheets, phash, palette) → registry
   └─ Claude ─────────────── extracts content, writes outline/spec, critic review of the preview
                                    │
                                    ▼
                    Supabase Storage "infographics" ◄── approved PNG, HTML, SVG, JPG, PDF
```

### Files

| Path | Purpose |
|---|---|
| `.claude/skills/infographic/SKILL.md` | The workflow Claude follows |
| `skill/registry.py` | The only code that touches the database |
| `skill/render.py` | Build (`build --spec`), icon search (`icons`), export (`export --html`) |
| `skill/brand.py` | Reads a brand pack |
| `skill/analyze.py` | Backfill: `prepare`, then Claude writes `tags.json`, then `finish` (preview, then `--yes`) |
| `skill/brands_sync.py` | `pull`, `submit`, `list`, and admin `review` / `approve` / `reject` |
| `skill/config.yaml` | Model, thresholds, render and critic settings |
| `skill/critic_rules.md` | Base design-quality rules (28 rules) |
| `skill/templates/` | `base`, `macros`, `vertical_list`, `horizontal_timeline`, `comparison_cards`, `cell_table`, `card_list`, `three_column_grid`, `custom` |
| `brands/_template/` | Starting point for a new client |
| `brands/fcc/` | `DESIGN.md` (v1.0.0), `critic_rules.md` (F1–F20), `assets/` (brand.css, canvas.svg, fonts), `past/` (20 SVGs), `source/FCC_rules.md` |
| `sql/schema.sql` | Tables `infographics` and `brand_packs`; safe to re-run (`registry.py init`) |
| `tests/test_registry.py` | Verdict rules, known topic blocked, duplicate pending warns, unrelated topic ok |
| `scripts/setup.sh`, `scripts/setup.ps1` | One-command setup for macOS/web and Windows |
| `docs/SUMMARY.md` | What each reference repo offers |

### Database (Supabase project `rtdhmkhccecsqpdvleaf`, region ap-south-1)
- **`infographics`:** client, topic, angle, key_points, layout_type, brand_version, embedding, topic_embedding, phash,
  png_url, html_url, source, status (`pending | approved | rejected | old_brand | review`), created_by, created_at.
  Row-level security is on (it blocks the public Data API; the skill connects directly).
- **`brand_packs`:** client, brand_version, status (`pending | approved | rejected`), files, notes, reviewer fields.
- **Storage buckets (private):** `infographics` (finished work), `brands` (brand packs).

---

## 5. FCC brand: what is in the registry

- **20 past infographics backfilled** (approved, brand v1.0.0), tagged by layout family. Because they were inserted
  together, the "last layout used" was the wholesale price index piece (`three_column_grid`) until new work was logged.
- **1 new infographic logged** in the end-to-end test: *How Retailers Can Launch a Retail Media Network*
  (`vertical_list/hex_icon`), with all exports. The critic caught empty hexagons in v1 (a CSS bug), and it was fixed in v2.
- **Layout families seen in FCC work:** vertical list (icon, number, hexagon, side rail), horizontal timeline (arrow,
  alternating), S-curve steps, hexagon zig-zag row, central spine, comparison cards (pill header, outline, VS, divider),
  cell table, card list (check, number), three-column grid. Also allowed: hub and spoke, pyramid, before/after, stat grid.

---

## 6. Environment and setup notes

- **`.env` keys:** `DATABASE_URL` (Session pooler URI), `SUPABASE_URL`, `SUPABASE_SECRET_KEY` (the legacy `service_role`
  key works), `DESIGNER`, and `BRAND_ADMIN=1` on the admin's machine only.
- **Gotchas we hit:**
  - A password with `@` must be written as `%40`.
  - The Supabase template's `[YOUR-PASSWORD]` brackets must be removed.
  - The line must not start with `DATABASE_URL=` twice.
  - The publishable key cannot upload; use the secret key.
- **Supabase dashboard:** reset the database password under Database → Settings, or via the Connect dialog.
  Turn on the `vector` extension.
- **Python 3.12 environment in `.venv`** (CPU-only torch). Playwright Chromium handles rendering.
- **Editor config:** `pyproject.toml` puts `skill/` on the path for pytest, Pyrefly and Pyright.
- **This laptop:** the disk on `/home` is tight. Clear caches (`uv cache clean`, `npm cache clean --force`) when needed.
  The GTX 1650 runs on the nouveau driver (no CUDA); don't change drivers without asking.

---

## 7. How to do common things

| Task | How |
|---|---|
| Make an infographic | In Claude Code inside the repo: "make an FCC infographic from this: …" |
| Add a client | "Set up a new client called X from this brand guide" + old infographics → you approve the backfill → submitted for admin review |
| Approve brands (admin) | "Review pending brands" (needs `BRAND_ADMIN=1`) |
| Update a brand | Edit the pack, bump `brand_version` + `updated`, then submit again |
| Rebrand | Bump the version, then mark old rows `old_brand` (they still block repeats) |
| Re-export a version | `skill/render.py export --html output/<client>/<slug>/vN.html --formats svg,jpeg,pdf` |
| Run tests | `.venv/bin/python -m pytest -q` |
| Install on a new laptop | See README "Install" (Mac, Windows, web), or ask Claude Code to "clone and set it up" |

---

## 8. Open items / ideas

- **Pending cleanup:** abandoned pending rows stop blocking after 7 days but stay in the table; a cleanup command could delete them.
- **Real admin security:** `BRAND_ADMIN` is a guard against mistakes, not security. For real separation, create the
  restricted `designer` database role (commented in `schema.sql`).
- **Reusable layouts:** S-curve, hexagon zig-zag and central spine currently render through `custom`; they could become templates.
- **Public repo:** `brands/fcc/past/` and `brands/fcc/source/` are public. Add them to `.gitignore` if they are confidential.
- **v2 (parked):** animated or web infographics using the animation repos in `reference/`.
- **ZIP installs don't update:** step 1's `git pull` only works for a clone. A designer who downloaded a ZIP gets brand
  updates (Supabase) but no code updates. Possible fix: an update script that downloads the latest ZIP when the folder
  is not a git repo, keeping `.env`, `.venv`, `output/` and `brands/`.
- **Output naming is not in the skill yet** (see section 9). Until it is added to SKILL.md, only `output/<client>/<slug>/vN.*` is produced.
- **False "font not loaded" warning:** the auto check probes weight 400 only, so pieces with no regular-weight text
  (e.g. the hub and formula pieces) always warn. Fix: check only the weights the page uses.
- **Fallback values match FCC:** `render.py` falls back to icon scale 0.6, stroke 1.5 and content width 1500 when a
  brand's DESIGN.md leaves them out. `brands/_template/` should state them so new clients don't inherit FCC's silently.
  The auto checks' 20px minimum text and always-allowed white apply to every brand.

---

## 9. Oct 28 session: test run and fixes

### Updates for designers without GitHub
- The repo is public, so anyone can `git clone` / `git pull` over **HTTPS** without an account (SSH needs one).
- Every job already runs `git pull --ff-only` (code) and `brands_sync.py pull` (approved brands) in step 1, so an
  approved brand reaches everyone on their next job with no action. Only ZIP installs miss code updates (section 8).

### Can the skill design without directions?
Yes. It infers the layout from the shape of the content, asks only when two shapes fit equally, builds any
requested shape through `custom`, and never repeats the previous layout family. It cannot invent a new visual
style: every layout stays inside the brand pack.

### Test run: 5 FCC pieces (not logged to the registry)
Dedup check found no repeats (#4 warned on "pricing" against *Building a value-based pricing strategy*, a different topic).

| Piece | Layout | Critic findings fixed |
|---|---|---|
| Top customer acquisition strategies for retailers | hub and spoke (`custom`) | middle connectors too short; icons too thick (see below) |
| How to calculate customer acquisition cost (CAC) | equation strip (`custom`) | "acquisition-" broke at the hyphen (non-breaking hyphen) |
| Why food and beverage pricing is challenging | `vertical_list/icon` | list hugged the left (centred with `width: auto`) |
| High-low pricing strategy in action | price-over-time chart (`custom`, inline SVG, no invented numbers) | stray `#000000` fill on lines |
| CDP vs CRM vs DMP | `cell_table` | table too narrow, 4–5 line cells (widened to 1720px) |

### Output naming (agreed with the designer)
Final files are copied to `output/` (git-ignored) as `<kind> - <alt text>.<ext>`, where kind is `infographic` or `table`.
Without alt text: `<kind> - <date>`; with more than one of that kind for the client on the same day:
`<kind> - <number> - <date>`. Same name for PNG, SVG, JPEG and PDF.

### Fixes in code
- **Icon thickness in custom layouts:** custom markup pasted icons at full tile size, skipping the brand's 0.6 scale,
  so strokes were about 1.7× too heavy. `render.py` now renders custom `html` through Jinja so `icon()` applies the
  brand scale and stroke; SKILL.md step 7 says to use it.
- **Pyrefly errors in `render.py` (10):** typed `GLOBALS` / `BRAND_DIR` instead of untyped Jinja globals,
  `Image.Resampling.LANCZOS`, a clear error when exporting a page not made by `render.py`, explicit PDF margins.
  Output is byte-identical; tests pass.
- **Audit:** no FCC rules are hard-coded in `render.py` or the templates; everything comes from the brand pack.

# Reference repos: what each gives a static infographic skill

All repos are read-only inspiration. Nothing here is installed or executed.

## Core for v1

**google-labs-code/design.md** (DESIGN.md format)
- The spec (`docs/spec.md`): YAML tokens (front matter or fenced blocks) + markdown prose.
- Token groups: `colors`, `typography`, `rounded`, `spacing`, `components`; `{path.to.token}` references.
- Fixed section order: Overview, Colors, Typography, Layout, Elevation, Shapes, Components, Do's and Don'ts.
- Has a linter (`npx @google/design.md lint`) with WCAG contrast checks; we can mirror the contrast check in Python.
- Use: base format for `brands/<client>/DESIGN.md`; we add an `infographic` block (canvas, layouts).

**VoltAgent/awesome-design-md** (84 real-brand DESIGN.md files)
- Worked examples of real brands (Ferrari, Tesla, Cal, Warp, HP...) written in the DESIGN.md format.
- Shows how much prose vs tokens a good brand pack carries, and how Do's/Don'ts are phrased.
- Use: reference when converting a client's brand rules (e.g. FCC_rules.md) into a DESIGN.md.

**nextlevelbuilder/ui-ux-pro-max-skill** (palette, type, style knowledge)
- CSV data: `colors.csv` (193 product-type palettes with on-colors), `typography.csv` (75 pairings), `styles.csv` (89 styles), `charts.csv` (26 chart-type rules).
- Use: fallback only when a brand pack is thin (missing secondary colors, chart guidance).
- `charts.csv` is directly useful for choosing stat/comparison visuals in infographics.

**Leonxlnx/taste-skill** (anti-generic rules)
- "Laws of the craft": 2-3 visible type sizes, max 5 sizes, one ground/one ink/one accent.
- Equal outer margins, one grid, larger gaps between sections than within them.
- Bans icon feature-card grids and pill badges as defaults; running text in full ink, never soft grey.
- Use: hierarchy, spacing and colour-discipline checks in critic_rules.md.

**pbakaus/impeccable** (design quality, critique)
- `craft-floor.md`: verify contrast (4.5:1 / 3:1), spacing rhythm, type floor, text overflow, copy.
- "Refuse" list: identical card grids, hero-metric template, eyebrows, gradient text, glass, side-stripe borders, emoji icons.
- Key principle: "the brief wins" — a pinned brand overrides taste warnings. Matches our DESIGN.md-first approach.
- Use: critic checklist and the critique scoring structure.

**Nutlope/hallmark** (anti-generic floor)
- "The Floor": all colours/fonts via `:root` tokens, no literal hex past the token block.
- Bans: invented metrics/testimonials, tracked-caps eyebrow labels, purple-blue gradients, card-in-card, emoji icons.
- ~80 words per screen guideline; one idea per screen; deal a direction so consecutive builds don't converge.
- Use: token discipline in render.py templates, "no invented numbers" rule, layout rotation idea.

**emilkowalski/skills** (design engineering)
- Mostly animation/interaction (springs, easing, gestures) — not relevant to static PNGs.
- Useful bits: "unseen details compound" (alignment, optical spacing), required review format (before/after table).
- Use: critic output format only. Rest parked for v2.

**nexu-io/open-design** (workflow structure)
- Agent design workspace: brief → design system → prototype → share → refine loop.
- Skills split into functional skills vs rendering `design-templates/`; mirrors our skill/ vs templates/ split.
- Relevant skills to skim: `design-brief`, `brand-extract`, `data-report`, `creative-director`.
- Use: shape of our SKILL.md (brief, outline gate, render, critique, approve).

## Parked for v2 (animation / components)

- **DavidHDev/react-bits** — animated React components. Parked.
- **magicuidesign/magicui** — animated React/Tailwind components. Parked.
- **greensock/gsap-skills** — GSAP animation skills. Parked.
- **oso95/scroll-world** — scroll-driven scenes. Parked.
- **DavidHDev/canvas-ui** — canvas UI components. Parked.
- **enesozturk/dimensional-drawing** — 3D/dimensional drawing. Parked.

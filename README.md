# 91Ninjas Design Skills: Infographic Skill

A Claude Code skill that turns a piece of content into an on-brand client infographic.

You paste a content part (text or an image) and name the client. The skill then:

1. Loads that client's brand pack (`brands/<client>/DESIGN.md`).
2. Checks the shared registry so we **never make an infographic that already exists**.
3. Proposes an outline and layout → **you approve**.
4. Renders the infographic (HTML → PNG), and a critic loop fixes design problems (max 3 revisions).
5. Shows you the final PNG → **you approve**.
6. Saves it to the shared registry, so the whole team knows it exists.

Nothing is saved as final without your approval.

---

## Install

You need three things on every machine: **Git**, **Python 3.11 or newer**, and **Claude Code**.
Ask the admin for the three secret values that go in `.env` (see [Configure](#configure)).

### macOS

1. Install the tools (skip any you already have):
   ```bash
   xcode-select --install                             # Git
   brew install python@3.12                           # or download from python.org
   curl -fsSL https://claude.ai/install.sh | bash     # Claude Code
   ```
2. Get the repo and run setup (takes about 3–5 minutes the first time):
   ```bash
   git clone https://github.com/Kawaii-Inosuke/91ninjas-designskills.git
   cd 91ninjas-designskills
   bash scripts/setup.sh
   ```
3. Fill in `.env` (setup created it), then start Claude Code in the folder:
   ```bash
   claude
   ```

### Windows

1. Install the tools:
   - **Git:** https://git-scm.com/download/win (default options).
   - **Python 3.12:** https://www.python.org/downloads/. On the first screen, tick **"Add python.exe to PATH"**.
   - **Claude Code:** open PowerShell and run `irm https://claude.ai/install.ps1 | iex`.
2. Get the repo and run setup in **PowerShell**:
   ```powershell
   git clone https://github.com/Kawaii-Inosuke/91ninjas-designskills.git
   cd 91ninjas-designskills
   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
   ```
3. Fill in `.env` (open it with Notepad: `notepad .env`), then start Claude Code:
   ```powershell
   claude
   ```

You can also use the Claude Code extension for VS Code or JetBrains. Open the cloned folder in the editor and the skill works the same way.

### Let Claude Code install it for you

Once Git, Python and Claude Code are installed, a designer can open Claude Code in any folder and say:

> Clone https://github.com/Kawaii-Inosuke/91ninjas-designskills.git and set it up.

Claude reads `CLAUDE.md` in the repo, runs the right setup script for the machine, and asks the designer to paste the secrets into `.env`. Secrets go in the file, never in the chat. Claude then checks the connection. After that, open Claude Code inside the repo folder to use the skill.

### Claude Code on the web (claude.ai/code)

1. Go to https://claude.ai/code and connect your GitHub account.
2. Choose the repo **Kawaii-Inosuke/91ninjas-designskills**.
3. In the environment settings:
   - **Environment variables:** add `DATABASE_URL`, `SUPABASE_URL` and `SUPABASE_SECRET_KEY` (same values as `.env`).
   - **Network access:** allow outbound internet. Setup downloads packages from `pypi.org`,
     `download.pytorch.org`, `huggingface.co` and the Playwright browser, and the skill talks to `*.supabase.co`.
4. Start a session. Your first message should be:
   > Run `bash scripts/setup.sh`
5. Then use the skill as normal (see [Use](#use)).

Web sessions start from a clean machine, so setup runs once per new session (a few minutes).
Approved infographics are uploaded to Supabase Storage, so you can download them from there afterwards.

---

## Configure

`.env` lives in the repo folder and is **never committed** (it's in `.gitignore`).

```
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SECRET_KEY=<secret key from Supabase → Project Settings → API Keys>
DESIGNER=<your name, shown on everything you make>
```

The admin shares these values through a password manager, never in Slack or email.
If the password contains `@`, write it as `%40` inside `DATABASE_URL`.

Check it works:
```bash
.venv/bin/python skill/registry.py list --client fcc --limit 3          # macOS / web
.venv\Scripts\python skill\registry.py list --client fcc --limit 3      # Windows
```

---

## Use

In Claude Code, inside the repo folder, ask in plain language:

> Make an FCC infographic from this: *(paste the content, or give an image path)*

Or call the skill directly: `/infographic fcc <content>`.

What happens:

| Step | What you see |
|---|---|
| Duplicate check | If it already exists, the skill stops and shows you the existing one. |
| Outline | Title, layout, every line of text, icons. **Approve or ask for changes.** |
| Direction | Only if the shape is unclear, it asks one question (e.g. "timeline or staircase?"). Any shape you ask for gets built. |
| Render + critic | It renders, checks against the brand rules, and fixes up to 3 times. |
| Final | Path to the PNG and HTML. **Approve, request changes, or abandon.** |
| Export | SVG, JPEG and PDF are created next to the PNG. |
| Log | Approved work and all exports are uploaded and registered for the whole team. |

Drafts are saved locally in `output/<client>/<topic>/` (v1, v2…).

### Export formats

| Format | Use it for |
|---|---|
| **SVG** | Small fixes by a designer. Text stays live and editable (Inter, correct weights) in Figma or Illustrator. |
| **PNG** | Default upload for social and blogs (exact pixels). |
| **JPEG** | Channels that only take JPEG. |
| **PDF** | Vector version for print or review. |

Export any version by hand: `.venv/bin/python skill/render.py export --html output/<client>/<topic>/v2.html --formats svg,jpeg,pdf`

The SVG uses the font by name. Figma has Inter built in. For Illustrator, install the fonts from `brands/<client>/assets/fonts/`.

---

## Clients (brand packs)

Each client is a folder in `brands/`:

```text
brands/<client>/
  DESIGN.md          brand tokens + rules (google design.md format), with brand_version and date
  critic_rules.md    the client's design checks (override the base rules)
  assets/brand.css   the client's look for the layout templates
  assets/fonts/      font files named <Family>-<weight>.woff2
  assets/icons/      optional icons (SVG); used before the built-in icon set
  past/              old infographics (SVG with live text, or PNG/JPEG) for backfill
  source/            the original brand guideline document
```

**Available now:** `fcc` (Flipkart Commerce Cloud), with 21 infographics in the registry.

### Add a new client

Ask Claude Code: *"Set up a new client called `<name>` from this brand guide"* and attach the guideline.
It copies `brands/_template/`, fills in the brand pack, and walks you through backfilling past work.
Brand changes go through a branch and a pull request; bump `brand_version` and `updated` every time.

---

## Repo layout

```text
.claude/skills/infographic/SKILL.md   the workflow Claude follows (two approval gates)
skill/registry.py                      shared registry: check, reserve, release, log, list, backfill
skill/analyze.py                       backfill old infographics (cheap contact-sheet analysis)
skill/render.py                        spec → HTML → PNG, automatic checks, revision limit
skill/brand.py                         reads DESIGN.md into tokens and CSS variables
skill/templates/                       layout families (structure only; brands style them)
skill/critic_rules.md                  base design-quality rules for every brand
skill/config.yaml                      embedding model, duplicate thresholds, output settings
skill/icons/                           Tabler icon set (MIT), restyled per brand
sql/schema.sql                         registry table (Supabase Postgres + pgvector)
scripts/setup.sh, scripts/setup.ps1    one-time setup
docs/SUMMARY.md                        notes on the design repos this skill learned from
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `password authentication failed` | Wrong password in `DATABASE_URL`, or a `@` not written as `%40`. |
| `invalid connection option` | The line starts with `DATABASE_URL=` twice. |
| Upload error `row-level security` | `SUPABASE_SECRET_KEY` holds the publishable key; use the secret key. |
| `.venv` not found | Run setup again (`scripts/setup.sh` or `scripts\setup.ps1`). |
| Windows: "running scripts is disabled" | Use `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1`. |
| Fonts look wrong in a PNG | The brand's `assets/fonts/` is missing a weight; the critic flags this as "font not loaded". |

Run the tests: `.venv/bin/python -m pytest tests -q`.

---

## For admins

- **Supabase:** the `infographics` table (`sql/schema.sql`, safe to re-run: `registry.py init`) and a private Storage bucket named `infographics`.
- **Thresholds** in `skill/config.yaml` were tuned on the FCC backfill (block ≥ 0.80, warn ≥ 0.65).
- **Rebrand:** bump `brand_version`, then mark older rows `old_brand`. They still block repeats but stop being style references.
- **Security:** keep `.env` out of Git. For a larger team, create the restricted `designer` database role (commented in `schema.sql`) instead of sharing the owner password.

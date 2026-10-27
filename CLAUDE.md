# Infographic skill repo

- Workflow: `.claude/skills/infographic/SKILL.md`. Code: `skill/` (Python, run with `.venv/bin/python`).
- Brand packs: `brands/<client>/` (DESIGN.md, critic_rules.md, assets/, past/). `brands/_template/` for new clients.
- `reference/` is read-only inspiration (git-ignored); never install or run it.
- Secrets only in `.env` (see `.env.example`). Never commit; the user commits manually.
- Setup: `uv venv .venv && uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu && uv pip install --python .venv/bin/python -r requirements.txt && .venv/bin/playwright install chromium`
- Tests: `.venv/bin/python -m pytest tests -q` (DB tests use throwaway `__pytest_*` clients).

# Infographic skill repo

- Workflow: `.claude/skills/infographic/SKILL.md`. Code: `skill/` (Python, run with `.venv/bin/python`).
- Brand packs: `brands/<client>/` (DESIGN.md, critic_rules.md, assets/, past/). `brands/_template/` for new clients.
- `reference/` is read-only inspiration (git-ignored); never install or run it.
- Secrets only in `.env` (see `.env.example`). Never commit; the user commits manually.
- Setup: `bash scripts/setup.sh` (macOS/Linux/web) or `scripts\setup.ps1` (Windows). Python is `.venv/bin/python` or `.venv\Scripts\python`.
- Tests: `.venv/bin/python -m pytest tests -q` (DB tests use throwaway `__pytest_*` clients).

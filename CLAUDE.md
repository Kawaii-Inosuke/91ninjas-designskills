# Infographic skill repo

- Workflow: `.claude/skills/infographic/SKILL.md`. Code: `skill/` (Python, run with `.venv/bin/python`, or `.venv\Scripts\python` on Windows).
- Brand packs: `brands/<client>/` (DESIGN.md, critic_rules.md, assets/, past/). `brands/_template/` for new clients.
- `reference/` is read-only inspiration (git-ignored); never install or run it.
- Secrets only in `.env` (see `.env.example`). Never commit `.env`; the repo owner commits manually.
- Tests: `.venv/bin/python -m pytest tests -q` (DB tests use throwaway `__pytest_*` clients).

## Installing for a new user (when asked to "install" or "set up" this repo)
1. Check prerequisites: `git`, Python 3.11+ (`python3 --version` / `py -3 --version`). If missing, tell the user what to
   install (README "Install") and ask before installing anything system-wide.
2. Run setup from the repo root: `bash scripts/setup.sh` (macOS/Linux/web) or
   `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1` (Windows). It creates `.venv`, installs packages,
   downloads Chromium and the embedding model, and creates `.env` from `.env.example`.
3. Ask the user to paste their `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SECRET_KEY` (from the admin) into `.env`
   themselves. Do not ask them to paste secrets into the chat. Suggest setting `DESIGNER=<their name>`.
4. Verify: `.venv/bin/python skill/registry.py list --client fcc --limit 1` returns JSON, and
   `.venv/bin/python -m pytest tests -q` passes.
5. Tell them how to use it: open Claude Code in this folder and say "make an FCC infographic from this: ...".
   The skill is project-scoped: it works when Claude Code runs inside this repo folder.

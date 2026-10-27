#!/usr/bin/env bash
# One-time setup for macOS / Linux / Claude Code on the web. Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f .venv/.setup-done ]; then echo "Setup already done."; exit 0; fi
if command -v uv >/dev/null; then
  uv venv -q .venv
  uv pip install -q --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu
  uv pip install -q --python .venv/bin/python -r requirements.txt
else
  python3 -m venv .venv
  .venv/bin/pip install -q torch --index-url https://download.pytorch.org/whl/cpu
  .venv/bin/pip install -q -r requirements.txt
fi
.venv/bin/playwright install chromium
.venv/bin/python -c "from sentence_transformers import SentenceTransformer as S; S('sentence-transformers/all-MiniLM-L6-v2')"
[ -f .env ] || { cp .env.example .env; echo "Created .env - fill in the values from your admin."; }
touch .venv/.setup-done
echo "Setup complete."

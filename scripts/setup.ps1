# One-time setup for Windows (PowerShell). Safe to re-run.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
if (Test-Path .venv\.setup-done) { Write-Host "Setup already done."; exit 0 }
$py = ".venv\Scripts\python.exe"
if (Get-Command uv -ErrorAction SilentlyContinue) {
  uv venv -q .venv
  uv pip install -q --python $py torch --index-url https://download.pytorch.org/whl/cpu
  uv pip install -q --python $py -r requirements.txt
} else {
  py -3 -m venv .venv
  & $py -m pip install -q torch --index-url https://download.pytorch.org/whl/cpu
  & $py -m pip install -q -r requirements.txt
}
& .venv\Scripts\playwright.exe install chromium
& $py -c "from sentence_transformers import SentenceTransformer as S; S('sentence-transformers/all-MiniLM-L6-v2')"
if (-not (Test-Path .env)) { Copy-Item .env.example .env; Write-Host "Created .env - fill in the values from your admin." }
New-Item -ItemType File .venv\.setup-done -Force | Out-Null
Write-Host "Setup complete."

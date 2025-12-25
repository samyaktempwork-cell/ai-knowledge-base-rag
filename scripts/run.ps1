$ErrorActionPreference = "Stop"

# Ensure env file exists
if (-not (Test-Path ".env")) {
  Write-Host "Missing .env file. Create it in repo root with OPENAI_API_KEY and settings."
  exit 1
}

# Run server using uv-managed venv
uv run uvicorn app.main:app --reload

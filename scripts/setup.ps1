$ErrorActionPreference = "Stop"

function Ensure-UvOnPath {
  $uvBin = Join-Path $env:USERPROFILE ".local\bin"
  if ($env:Path -notlike "*$uvBin*") {
    $env:Path = "$uvBin;$env:Path"
  }
}

# 1) Install uv if missing
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  Write-Host "uv not found. Installing uv..."
  irm https://astral.sh/uv/install.ps1 | iex

  # Make uv available in the CURRENT session
  Ensure-UvOnPath
}

# 2) Verify uv is callable
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  throw "uv installed but still not found on PATH. Restart PowerShell OR run: `$env:Path = `"$env:USERPROFILE\.local\bin;$env:Path`""
}

Write-Host "Setting up project with Python 3.12 and dependencies..."

# 3) Install Python 3.12 and create venv
uv python install 3.12
uv venv --python 3.12

# 4) Install dependencies (choose ONE approach)
# If using pyproject.toml (recommended):
uv sync

Write-Host "Setup complete."
Write-Host "Next: .\scripts\run.ps1"

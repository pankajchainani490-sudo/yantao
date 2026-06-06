$ErrorActionPreference = 'Stop'

Set-Location -LiteralPath "$PSScriptRoot\..\..\backend"

if (-not (Test-Path -LiteralPath ".venv")) {
  python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" "..\scripts\train\build_processed_dataset.py"
& ".\.venv\Scripts\python.exe" "..\scripts\train\train_models.py"
& ".\.venv\Scripts\python.exe" -m pytest -v

Set-Location -LiteralPath "$PSScriptRoot\..\..\frontend"
npm run build

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $RepoRoot "backend"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"
if (!(Test-Path $VenvPython)) { throw "Backend virtual environment not found. Create backend\.venv and install requirements-desktop.txt first." }
Push-Location $Backend
try {
    & $VenvPython -m pip install -r requirements-desktop.txt
    & $VenvPython -m PyInstaller --noconfirm --clean --onefile --name voicegrocery-backend --paths . --hidden-import pandas --hidden-import openpyxl run_server.py
} finally { Pop-Location }
if (!(Test-Path (Join-Path $Backend "dist\voicegrocery-backend.exe"))) { throw "PyInstaller did not create the backend executable." }
Write-Host "Backend executable created: backend\dist\voicegrocery-backend.exe"

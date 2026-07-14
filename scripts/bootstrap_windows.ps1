$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' was not found. Install 64-bit Python 3.11 or 3.12 first."
}

$PythonSelector = $null
foreach ($Candidate in @("-3.12", "-3.11")) {
    & py $Candidate -c "import sys; print(sys.version)" *> $null
    if ($LASTEXITCODE -eq 0) {
        $PythonSelector = $Candidate
        break
    }
}
if (-not $PythonSelector) {
    throw "Python 3.12 or 3.11 was not found through the Windows py launcher."
}

if (Test-Path .venv) {
    Write-Host "Reusing existing .venv. Delete it first when changing Python versions."
} else {
    & py $PythonSelector -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
& .\.venv\Scripts\python.exe -m pip install -e . -r requirements-windows-femm.txt

Write-Host ""
Write-Host "Environment ready at .venv using Python selector $PythonSelector"
Write-Host "FEMM itself must be installed on Windows in addition to the pyFEMM package."
Write-Host "Next command:"
Write-Host ".\.venv\Scripts\python.exe scripts\check_environment.py --config configs\one_eighth_100C.toml"

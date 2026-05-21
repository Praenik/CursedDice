param(
    [string]$PythonExe = (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe")
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvSitePackages = Join-Path $projectRoot ".venv\Lib\site-packages"
$specPath = Join-Path $projectRoot "CursedDice.spec"

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

if (-not (Test-Path $venvSitePackages)) {
    throw "Site-packages directory not found: $venvSitePackages"
}

$env:PYTHONPATH = $venvSitePackages

Push-Location $projectRoot
try {
    & $PythonExe -m PyInstaller --noconfirm --clean $specPath
}
finally {
    Pop-Location
}

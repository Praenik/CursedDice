param(
    [string]$PythonExe = (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe")
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sitePackages = Join-Path $projectRoot ".venv\Lib\site-packages"
$specPath = Join-Path $projectRoot "CursedDice.spec"

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

if (-not (Test-Path $sitePackages)) {
    throw "Site-packages directory not found: $sitePackages"
}

$env:PYTHONPATH = $sitePackages

Push-Location $projectRoot
try {
    & $PythonExe -m PyInstaller --noconfirm --clean $specPath
}
finally {
    Pop-Location
}

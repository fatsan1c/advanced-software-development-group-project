# Setup script for Paragon Apartments project
# This script resolves all paths from its own location, so it can be run from any directory.

$ErrorActionPreference = "Stop"

Write-Host "Setting up Paragon Apartments project..." -ForegroundColor Green

# Resolve paths relative to this script
$setupDir = $PSScriptRoot
$projectRoot = Split-Path -Parent $setupDir
$venvPath = Join-Path $projectRoot ".venv"
$venvScriptsPath = Join-Path $venvPath "Scripts"
$activateScriptPath = Join-Path $venvScriptsPath "Activate.ps1"
$requirementsPath = Join-Path $setupDir "requirements.txt"
$dbPath = Join-Path $projectRoot "paragonapartments\database\paragonapartments.db"
$seedScriptPath = Join-Path $setupDir "tools\create_sqlite_testdata.py"
$mainPath = Join-Path $projectRoot "paragonapartments\main.py"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found on PATH. Install Python and retry."
}

Push-Location $projectRoot
try {
    # Create virtual environment
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & python -m venv $venvPath

    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    if (-not (Test-Path $activateScriptPath)) {
        throw "Could not find activation script at: $activateScriptPath"
    }
    . $activateScriptPath

    # Upgrade pip
    Write-Host ""
    Write-Host "Upgrading pip..." -ForegroundColor Yellow
    & python -m pip install --upgrade pip

    # Install dependencies
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & python -m pip install -r $requirementsPath

    # Fix Tcl/Tk for virtual environment (Windows-specific fix for customtkinter)
    Write-Host ""
    Write-Host "Configuring Tcl/Tk for virtual environment..." -ForegroundColor Yellow
    $pythonBase = & python -c "import sys; print(sys.base_prefix)"
    $tclSource = Join-Path $pythonBase "tcl"
    $dllsSource = Join-Path $pythonBase "DLLs"

    if (Test-Path $tclSource) {
        Copy-Item $tclSource -Destination $venvPath -Recurse -Force
        Write-Host "Copied Tcl/Tk libraries to virtual environment" -ForegroundColor Green
    }

    if (Test-Path $dllsSource) {
        $tcl86 = Join-Path $dllsSource "tcl86t.dll"
        $tk86 = Join-Path $dllsSource "tk86t.dll"

        if (Test-Path $tcl86) {
            Copy-Item $tcl86 -Destination $venvScriptsPath -Force
        }
        if (Test-Path $tk86) {
            Copy-Item $tk86 -Destination $venvScriptsPath -Force
        }
        Write-Host "Copied Tcl/Tk DLL files to virtual environment" -ForegroundColor Green
    }

    # Create SQLite database (uses seed for full test data)
    Write-Host ""
    if (Test-Path $dbPath) {
        Write-Host "Database already exists, skipping creation..." -ForegroundColor Cyan
        Write-Host "To recreate with full data, run: python $seedScriptPath" -ForegroundColor Gray
    } else {
        Write-Host "Creating SQLite database with seed data..." -ForegroundColor Yellow
        & python $seedScriptPath
    }

    Write-Host ""
    Write-Host "Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run: python $mainPath"
    Write-Host ""
    Write-Host "To activate the virtual environment later, run:" -ForegroundColor Cyan
    Write-Host $activateScriptPath
}
finally {
    Pop-Location
}
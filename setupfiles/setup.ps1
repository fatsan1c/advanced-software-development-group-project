# Setup script for Paragon Apartments project
# Run this script from the setupfiles directory to set up the project automatically

Write-Host "Setting up Paragon Apartments project..." -ForegroundColor Green

# Navigate to project root
Set-Location ..

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r setupfiles\requirements.txt

# Fix Tcl/Tk for virtual environment (Windows-specific fix for customtkinter)
Write-Host ""
Write-Host "Configuring Tcl/Tk for virtual environment..." -ForegroundColor Yellow
$pythonBase = python -c "import sys; print(sys.base_prefix)"
$tclSource = Join-Path $pythonBase "tcl"
$dllsSource = Join-Path $pythonBase "DLLs"

if (Test-Path $tclSource) {
    Copy-Item $tclSource -Destination ".venv\" -Recurse -Force
    Write-Host "Copied Tcl/Tk libraries to virtual environment" -ForegroundColor Green
}

if (Test-Path $dllsSource) {
    $tcl86 = Join-Path $dllsSource "tcl86t.dll"
    $tk86 = Join-Path $dllsSource "tk86t.dll"
    
    if (Test-Path $tcl86) {
        Copy-Item $tcl86 -Destination ".venv\Scripts\" -Force
    }
    if (Test-Path $tk86) {
        Copy-Item $tk86 -Destination ".venv\Scripts\" -Force
    }
    Write-Host "Copied Tcl/Tk DLL files to virtual environment" -ForegroundColor Green
}

# # Create SQLite database
# Write-Host ""
# Write-Host "Creating SQLite database..." -ForegroundColor Yellow
# python setupfiles\create_sqlite_db.py

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: python paragonapartments\main.py"
Write-Host ""
Write-Host "To activate the virtual environment later, run:" -ForegroundColor Cyan
Write-Host ".\.venv\Scripts\Activate.ps1"

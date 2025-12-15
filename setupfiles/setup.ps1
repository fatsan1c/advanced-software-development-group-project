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

# Create .env file if it doesn't exist
if (!(Test-Path "paragonapartments\.env")) {
    Write-Host ""
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item "paragonapartments\.env.example" "paragonapartments\.env"
    Write-Host "IMPORTANT: Edit paragonapartments\.env with your database credentials!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit paragonapartments\.env with your database credentials"
Write-Host "2. Run: python paragonapartments\main.py"
Write-Host ""
Write-Host "To activate the virtual environment later, run:" -ForegroundColor Cyan
Write-Host ".\.venv\Scripts\Activate.ps1"

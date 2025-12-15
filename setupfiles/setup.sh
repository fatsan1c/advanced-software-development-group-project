#!/bin/bash
# Setup script for Paragon Apartments project (Linux/Mac)
# Run this script from the setupfiles directory to set up the project automatically

echo -e "\033[0;32mSetting up Paragon Apartments project...\033[0m"

# Navigate to project root
cd ..

# Create virtual environment
echo -e "\n\033[0;33mCreating virtual environment...\033[0m"
python3 -m venv .venv

# Activate virtual environment
echo -e "\033[0;33mActivating virtual environment...\033[0m"
source .venv/bin/activate

# Upgrade pip
echo -e "\n\033[0;33mUpgrading pip...\033[0m"
python -m pip install --upgrade pip

# Install dependencies
echo -e "\n\033[0;33mInstalling dependencies...\033[0m"
pip install -r setupfiles/requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "paragonapartments/.env" ]; then
    echo -e "\n\033[0;33mCreating .env file from template...\033[0m"
    cp paragonapartments/.env.example paragonapartments/.env
    echo -e "\033[0;31mIMPORTANT: Edit paragonapartments/.env with your database credentials!\033[0m"
fi

echo -e "\n\033[0;32m✓ Setup complete!\033[0m"
echo -e "\n\033[0;36mNext steps:\033[0m"
echo "1. Edit paragonapartments/.env with your database credentials"
echo "2. Run: python paragonapartments/main.py"
echo -e "\n\033[0;36mTo activate the virtual environment later, run:\033[0m"
echo "source .venv/bin/activate"

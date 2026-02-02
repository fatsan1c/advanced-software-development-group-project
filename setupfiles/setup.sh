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

# Create SQLite database
echo ""
DB_PATH="paragonapartments/database/paragonapartments.db"
if [ -f "$DB_PATH" ]; then
    echo -e "\033[0;36mDatabase already exists, skipping creation...\033[0m"
    echo -e "\033[0;90mTo recreate the database, run: python setupfiles/tools/create_sqlite_db.py\033[0m"
else
    echo -e "\033[0;33mCreating SQLite database...\033[0m"
    python setupfiles/tools/create_sqlite_db.py
fi

echo -e "\n\033[0;32m✓ Setup complete!\033[0m"
echo -e "\n\033[0;36mNext steps:\033[0m"
echo "1. Run: python paragonapartments/main.py"
echo -e "\n\033[0;36mTo activate the virtual environment later, run:\033[0m"
echo "source .venv/bin/activate"

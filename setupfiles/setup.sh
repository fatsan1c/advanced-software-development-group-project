#!/bin/bash
# Setup script for Paragon Apartments project (Linux/Mac)
# This script resolves paths from its own location, so it can be run from any directory.

set -euo pipefail

# Resolve script and project paths
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
ACTIVATE_PATH="$VENV_PATH/bin/activate"
REQUIREMENTS_PATH="$SCRIPT_DIR/requirements.txt"
DB_PATH="$PROJECT_ROOT/paragonapartments/database/paragonapartments.db"
SEED_SCRIPT_PATH="$SCRIPT_DIR/tools/create_sqlite_testdata.py"
MAIN_PATH="$PROJECT_ROOT/paragonapartments/main.py"

echo -e "\033[0;32mSetting up Paragon Apartments project...\033[0m"

# Navigate to project root for predictable command behavior
cd "$PROJECT_ROOT"

if ! command -v python3 >/dev/null 2>&1; then
    echo -e "\033[0;31mError: python3 was not found on PATH.\033[0m"
    exit 1
fi

# Create virtual environment
echo -e "\n\033[0;33mCreating virtual environment...\033[0m"
python3 -m venv "$VENV_PATH"

# Activate virtual environment
echo -e "\033[0;33mActivating virtual environment...\033[0m"
if [ ! -f "$ACTIVATE_PATH" ]; then
    echo -e "\033[0;31mError: activation script not found at $ACTIVATE_PATH\033[0m"
    exit 1
fi
source "$ACTIVATE_PATH"

# Upgrade pip
echo -e "\n\033[0;33mUpgrading pip...\033[0m"
python -m pip install --upgrade pip

# Install dependencies
echo -e "\n\033[0;33mInstalling dependencies...\033[0m"
python -m pip install -r "$REQUIREMENTS_PATH"

# Create SQLite database
echo ""
if [ -f "$DB_PATH" ]; then
    echo -e "\033[0;36mDatabase already exists, skipping creation...\033[0m"
    echo -e "\033[0;90mTo recreate the database, run: python $SEED_SCRIPT_PATH\033[0m"
else
    echo -e "\033[0;33mCreating SQLite database...\033[0m"
    python "$SEED_SCRIPT_PATH"
fi

echo -e "\n\033[0;32m✓ Setup complete!\033[0m"
echo -e "\n\033[0;36mNext steps:\033[0m"
echo "1. Run: python $MAIN_PATH"
echo -e "\n\033[0;36mTo activate the virtual environment later, run:\033[0m"
echo "source $ACTIVATE_PATH"
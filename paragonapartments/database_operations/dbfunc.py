import sqlite3
import os
from pathlib import Path

# Get the project root (paragonapartments directory) and database path
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "database" / "paragonapartments.db"


# Database connection function
def getConnection():
    try:
        # Allow tests / tooling to override DB location
        override = os.environ.get("PAMS_DB_PATH")
        db_path = Path(override).expanduser().resolve() if override else DB_PATH

        # Check if database file exists
        if not db_path.exists():
            print(f"Database does not exist at: {db_path}")
            print("Run setupfiles/tools/create_sqlite_testdata.py to create the database")
            return None

        # Connect to SQLite database
        conn = sqlite3.connect(str(db_path))

        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")

        # Set row factory to return dict-like rows
        conn.row_factory = sqlite3.Row

        return conn

    except sqlite3.Error as err:
        print(f"SQLite Error: {err}")
        return None

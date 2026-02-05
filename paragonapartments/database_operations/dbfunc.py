import sqlite3
from pathlib import Path

# Get the project root (paragonapartments directory) and database path
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / 'database' / 'paragonapartments.db'

# Database connection function
def getConnection():    
    try:
        # Check if database file exists
        if not DB_PATH.exists():
            print(f'Database does not exist at: {DB_PATH}')
            print('Run setupfiles/create_sqlite_db.py to create the database')
            return None
        
        # Connect to SQLite database
        conn = sqlite3.connect(str(DB_PATH))
        
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Set row factory to return dict-like rows
        conn.row_factory = sqlite3.Row
        
        return conn
        
    except sqlite3.Error as err:
        print(f'SQLite Error: {err}')
        return None   
                

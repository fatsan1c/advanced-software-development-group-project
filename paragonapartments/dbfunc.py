import sqlite3
import os

# SQLite database path (relative to this file)
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'paragonapartments.db')

def getConnection():    
    try:
        # Check if database file exists
        if not os.path.exists(DB_PATH):
            print(f'Database does not exist at: {DB_PATH}')
            print('Run setupfiles/create_sqlite_db.py to create the database')
            return None
        
        # Connect to SQLite database
        conn = sqlite3.connect(DB_PATH)
        
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Set row factory to return dict-like rows
        conn.row_factory = sqlite3.Row
        
        return conn
        
    except sqlite3.Error as err:
        print(f'SQLite Error: {err}')
        return None   
                

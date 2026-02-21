"""
Database Helper - Centralized database query execution.
Provides a single function for executing all database queries with proper connection handling.
"""

import sqlite3
import sys
import os

# Add parent directory to path to import dbfunc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_operations.dbfunc import getConnection


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Execute a database query with proper connection handling.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Query parameters for parameterized queries
        fetch_one (bool): Return single row as dict
        fetch_all (bool): Return all rows as list of dicts
        commit (bool): Whether to commit the transaction (for INSERT/UPDATE/DELETE)
        
    Returns:
        - If fetch_one: dict or None
        - If fetch_all: list of dicts or []
        - If commit: last inserted ID or row count
        
    Raises:
        sqlite3.IntegrityError: For constraint violations (e.g., duplicate username)
        sqlite3.Error: For other database errors
        Exception: For unexpected errors
    """
    conn = None
    cursor = None
    
    try:
        conn = getConnection()
        if not conn:
            raise sqlite3.Error("Failed to establish database connection")
        
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        
        # Process results based on flags
        if fetch_one:
            row = cursor.fetchone()
            result = dict(row) if row else None
        elif fetch_all:
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
        elif commit:
            conn.commit()
            result = cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        else:
            result = None
            
        return result
        
    # Re-raise exceptions with original error info
    except sqlite3.IntegrityError as err:
        # Constraint violations (UNIQUE, FOREIGN KEY, etc.)
        print(f"Database integrity error: {err}")
        raise
    except sqlite3.Error as err:
        # Other database errors
        print(f"Database error: {err}")
        raise
    except Exception as e:
        # Unexpected errors
        print(f"Unexpected error: {e}")
        raise
    finally:
        # Ensure resources are cleaned up
        if cursor:
            cursor.close()
        if conn:
            conn.close()
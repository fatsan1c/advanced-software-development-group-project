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
        - None on error
    """
    conn = None
    cursor = None
    
    try:
        conn = getConnection()
        if not conn:
            return None if fetch_one else ([] if fetch_all else None)
        
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        
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
        
    except sqlite3.Error as err:
        print(f"Database error: {err}")
        return None if fetch_one else ([] if fetch_all else None)
    except Exception as e:
        print(f"Error: {e}")
        return None if fetch_one else ([] if fetch_all else None)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
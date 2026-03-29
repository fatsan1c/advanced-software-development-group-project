"""
Database Helper - Centralized database query execution.
Provides a single function for executing all database queries with proper connection handling.
"""

import sqlite3
from collections.abc import Callable
from typing import Any

# from database_operations.dbfunc import default_connection_manager


class DatabaseQueryExecutor:
    """
    Execute queries while owning connection and cursor lifecycle.
    """

    def __init__(self, connection_provider: Callable[[], sqlite3.Connection]):
        self.connection_provider = connection_provider

    def _process_results(
        self,
        cursor: sqlite3.Cursor,
        conn: sqlite3.Connection,
        *,
        fetch_one: bool,
        fetch_all: bool,
        commit: bool,
    ) -> Any:
        # Keep return-shape logic isolated for easier maintenance.
        if fetch_one:
            row = cursor.fetchone()
            return dict(row) if row else None

        if fetch_all:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        if commit:
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

        return None

    def execute_query(
        self,
        query: str,
        params: tuple[Any, ...] | None = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
        commit: bool = False,
    ) -> Any:
        """
        Execute a database query with proper connection handling.

        Args:
            query: SQL query to execute
            params: Query parameters for parameterized queries
            fetch_one: Return single row as dict
            fetch_all: Return all rows as list of dicts
            commit: Whether to commit the transaction (for INSERT/UPDATE/DELETE)

        Returns:
            - If fetch_one: dict or None
            - If fetch_all: list of dicts or []
            - If commit: last inserted ID or row count

        Raises:
            sqlite3.IntegrityError: For constraint violations (e.g., duplicate username)
            sqlite3.Error: For other database errors
            Exception: For unexpected errors
        """
        conn: sqlite3.Connection | None = None
        cursor: sqlite3.Cursor | None = None

        try:
            conn = self.connection_provider()
            if not conn:
                raise sqlite3.Error("Failed to establish database connection")

            cursor = conn.cursor()
            cursor.execute(query, params or ())

            return self._process_results(
                cursor,
                conn,
                fetch_one=fetch_one,
                fetch_all=fetch_all,
                commit=commit,
            )

        # Re-raise exceptions with original error info
        except sqlite3.IntegrityError as err:
            # Constraint violations (UNIQUE, FOREIGN KEY, etc.)
            print(f"Database integrity error: {err}")
            raise
        except sqlite3.Error as err:
            # Other database errors
            print(f"Database error: {err}")
            raise
        except Exception as err:
            # Unexpected errors
            print(f"Unexpected error: {err}")
            raise
        finally:
            # Ensure resources are cleaned up
            if cursor:
                cursor.close()
            if conn:
                conn.close()
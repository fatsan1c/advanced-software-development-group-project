import sqlite3
from pathlib import Path

class SQLiteConnectionManager:
    """
    Manage SQLite connection creation and configuration.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def _database_exists(self) -> bool:
        return self.db_path.exists()

    def _configure_connection(self, conn: sqlite3.Connection) -> sqlite3.Connection:
        # Keep DB safety/shape rules in one place.
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def get_connection(self) -> sqlite3.Connection | None:
        """
        Create and return a configured SQLite connection.
        """
        try:
            if not self._database_exists():
                print(f"Database does not exist at: {self.db_path}")
                print("Run setupfiles/create_sqlite_db.py to create the database")
                return None

            conn = sqlite3.connect(str(self.db_path))
            return self._configure_connection(conn)

        except sqlite3.Error as err:
            print(f"SQLite Error: {err}")
            return None                

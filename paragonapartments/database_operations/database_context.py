"""
Repository context - central wiring for database access dependencies.
"""

from database_operations.db_execute import DatabaseQueryExecutor
from database_operations.db_connection import SQLiteConnectionManager
from pathlib import Path

# Get the project root (paragonapartments directory) and database path
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "database" / "paragonapartments.db"

connection = SQLiteConnectionManager(DB_PATH)
query_executor = DatabaseQueryExecutor(connection.get_connection)
execute_query = query_executor.execute_query
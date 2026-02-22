"""
View SQLite Database Contents
This script reads and displays all data from the paragonapartments.db database.

Usage:
    python setupfiles/view_database.py              # View all data (all tables)
    python setupfiles/view_database.py --stats      # View statistics only
    python setupfiles/view_database.py --table NAME # View specific table
    python setupfiles/view_database.py --help       # Show help message

Examples:
    python setupfiles/view_database.py --table users
    python setupfiles/view_database.py --table apartments
    python setupfiles/view_database.py --table tenants
    python setupfiles/view_database.py --table lease_agreements
"""

import sqlite3
import os
from datetime import datetime

# Path to the SQLite database
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "paragonapartments",
    "database",
    "paragonapartments.db",
)


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_table_header(table_name):
    """Print a formatted table header."""
    print_separator()
    print(f"TABLE: {table_name.upper()}")
    print_separator()


def format_value(value, max_length=30):
    """Format a value for display, truncating if necessary."""
    if value is None:
        return "NULL"
    str_value = str(value)
    if len(str_value) > max_length:
        return str_value[: max_length - 3] + "..."
    return str_value


def display_table(cursor, table_name):
    """Display all contents of a table."""
    print_table_header(table_name)

    # Get all rows
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        print("(No data)")
        print()
        return

    # Get column names
    column_names = [description[0] for description in cursor.description]

    # Calculate column widths
    col_widths = {}
    for col in column_names:
        col_widths[col] = len(col)

    for row in rows:
        for col, value in zip(column_names, row):
            col_widths[col] = max(col_widths[col], len(format_value(value)))

    # Print column headers
    header = " | ".join(col.ljust(col_widths[col]) for col in column_names)
    print(header)
    print("-" * len(header))

    # Print rows
    for row in rows:
        row_str = " | ".join(
            format_value(value).ljust(col_widths[col])
            for col, value in zip(column_names, row)
        )
        print(row_str)

    print(f"\nTotal rows: {len(rows)}")
    print()


def get_database_stats(cursor):
    """Get and display database statistics."""
    print_separator("=")
    print("DATABASE STATISTICS")
    print_separator("=")

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{table_name.ljust(25)}: {count} rows")

    print()


def view_database(detailed=True, table_name=None):
    """
    View database contents.

    Args:
        detailed (bool): If True, show all data. If False, just show statistics.
        table_name (str): If provided, only show this specific table.
    """
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("Run 'python setupfiles/tools/create_sqlite_testdata.py' to create the database.")
        return

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    print()
    print("=" * 80)
    print("PARAGON APARTMENTS DATABASE VIEWER")
    print(f"Database: {os.path.basename(DB_PATH)}")
    print(
        f"Last modified: {datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"Size: {os.path.getsize(DB_PATH) / 1024:.2f} KB")
    print("=" * 80)
    print()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]

    # Show statistics
    get_database_stats(cursor)

    # Show detailed data if requested
    if detailed:
        if table_name:
            # Show specific table
            if table_name in table_names:
                display_table(cursor, table_name)
            else:
                print(f"❌ Table '{table_name}' not found.")
                print(f"Available tables: {', '.join(table_names)}")
        else:
            # Show all tables
            print_separator("=")
            print("TABLE CONTENTS")
            print_separator("=")
            print()

            for table in table_names:
                display_table(cursor, table)

    conn.close()
    print_separator("=")
    print("✓ Database view complete")
    print_separator("=")


def main():
    """Main function with menu options."""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats":
            # Show only statistics
            view_database(detailed=False)
        elif sys.argv[1] == "--table" and len(sys.argv) > 2:
            # Show specific table
            view_database(detailed=True, table_name=sys.argv[2])
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python view_database.py              # View all data")
            print("  python view_database.py --stats      # View statistics only")
            print("  python view_database.py --table NAME # View specific table")
            print("  python view_database.py --help       # Show this help")
        else:
            print("Unknown option. Use --help for usage information.")
    else:
        # Show everything by default
        view_database(detailed=True)


if __name__ == "__main__":
    main()

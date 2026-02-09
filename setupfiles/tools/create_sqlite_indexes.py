"""
Create SQLite Indexes for Performance

Adds indexes to the existing `paragonapartments.db` to speed up common finance queries.

Usage:
  python setupfiles/tools/create_sqlite_indexes.py
"""

import os
import sqlite3


DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "paragonapartments",
    "database",
    "paragonapartments.db",
)


INDEX_STATEMENTS = [
    # Invoices
    "CREATE INDEX IF NOT EXISTS idx_invoices_tenant ON invoices(tenant_ID)",
    "CREATE INDEX IF NOT EXISTS idx_invoices_paid_due ON invoices(paid, due_date)",
    # Payments
    "CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_ID)",
    # Lease agreements (used for city joins)
    "CREATE INDEX IF NOT EXISTS idx_lease_tenant_active ON lease_agreements(tenant_ID, active)",
]


def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    for stmt in INDEX_STATEMENTS:
        cur.execute(stmt)

    conn.commit()
    conn.close()
    print(f"OK: Indexes created (if missing) on {DB_PATH}")


if __name__ == "__main__":
    main()


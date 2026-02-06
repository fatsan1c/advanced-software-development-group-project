"""
Seed Finance Test Data (Invoices + Payments)

This tool inserts finance test data into the existing SQLite database:
  - invoices (50 by default)
  - payments for a subset of invoices (30 by default), also marks those invoices as paid
  - GUARANTEES a subset of invoices are unpaid AND overdue (late) for UI testing

It is designed to support Finance Manager UI testing across all locations.

Usage:
  python setupfiles/tools/seed_finance_testdata.py --reset --invoices 50 --paid 30 --late-unpaid 15
  python setupfiles/tools/seed_finance_testdata.py --invoices 50 --paid 20
"""

from __future__ import annotations

import argparse
import os
import random
import sqlite3
from datetime import date, timedelta


# Path to the SQLite database file
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "paragonapartments",
    "database",
    "paragonapartments.db",
)


def _connect():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at: {DB_PATH}\n"
            "Create it first (e.g. run setupfiles/tools/create_sqlite_testdata.py)"
        )
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _fetch_active_leases(conn):
    """
    Returns a list of dicts with tenant_id, monthly_rent, city.
    City is derived via lease -> apartment -> location.
    """
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            la.tenant_ID AS tenant_id,
            la.monthly_rent AS monthly_rent,
            l.city AS city
        FROM lease_agreements la
        JOIN apartments a ON la.apartment_ID = a.apartment_ID
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE la.active = 1
        ORDER BY l.city, la.tenant_ID
        """
    )
    return [dict(r) for r in cur.fetchall()]


def _table_row_count(conn, table):
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return int(cur.fetchone()[0])


def seed_finance_data(
    invoices_to_create: int = 50,
    paid_to_create: int = 30,
    late_unpaid_to_create: int = 15,
    reset: bool = False,
    seed: int = 42,
):
    """
    Seed invoices/payments into the DB.

    Args:
        invoices_to_create: number of invoice rows to insert
        paid_to_create: number of invoices that will also get a payment row and be marked paid
        late_unpaid_to_create: number of invoices that will be unpaid AND overdue (due_date < today)
        reset: if True, deletes existing payments + invoices first
        seed: random seed for repeatable data
    """
    random.seed(seed)

    conn = _connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    before_counts = {
        "invoices": _table_row_count(conn, "invoices"),
        "payments": _table_row_count(conn, "payments"),
    }

    if reset:
        # Payments references invoices, so delete payments first.
        cur.execute("DELETE FROM payments")
        cur.execute("DELETE FROM invoices")
        conn.commit()

    leases = _fetch_active_leases(conn)
    if not leases:
        raise RuntimeError("No active leases found; cannot distribute finance data across locations.")

    # Group tenants by city so we can distribute paid/late/unpaid across all locations.
    city_to_tenants = {}
    for row in leases:
        city = row.get("city") or "(no_city)"
        city_to_tenants.setdefault(city, []).append((int(row["tenant_id"]), float(row["monthly_rent"])))
    cities = sorted(city_to_tenants.keys())
    city_idx = {c: 0 for c in cities}

    def next_tenant_for_city(city: str):
        """Round-robin tenants within a city."""
        tenant_list = city_to_tenants[city]
        idx = city_idx[city] % len(tenant_list)
        city_idx[city] += 1
        return tenant_list[idx]

    # Generate invoices across recent months/weeks so we get a mix of late + upcoming
    today = date.today()
    invoice_rows = []
    # Normalize requested counts
    invoices_to_create = int(max(0, invoices_to_create))
    paid_to_create = int(max(0, min(paid_to_create, invoices_to_create)))
    remaining_after_paid = invoices_to_create - paid_to_create
    late_unpaid_to_create = int(max(0, min(late_unpaid_to_create, remaining_after_paid)))

    def make_invoice_row(tenant_id: int, rent: float, paid_flag: int, force_late: bool):
        if paid_flag == 1:
            # Paid: spread over last ~120 days
            issue_offset_days = random.randint(0, 120)
            issue_date = today - timedelta(days=issue_offset_days)
            due_date = issue_date + timedelta(days=random.choice([7, 14, 21, 28]))
        elif force_late:
            # Late unpaid: due_date before today, keep ordering sane
            issue_offset_days = random.randint(45, 160)
            issue_date = today - timedelta(days=issue_offset_days)
            due_date = today - timedelta(days=random.randint(1, 45))
            if due_date <= issue_date:
                # push issue_date further back to preserve due > issue
                issue_date = due_date - timedelta(days=random.randint(7, 28))
        else:
            # Upcoming unpaid: due date in the next ~45 days
            issue_offset_days = random.randint(0, 30)
            issue_date = today - timedelta(days=issue_offset_days)
            due_date = today + timedelta(days=random.randint(1, 45))

        amount_due = max(50.0, round(rent + random.uniform(-25, 75), 2))
        return {
            "tenant_id": int(tenant_id),
            "amount_due": float(amount_due),
            "issue_date": issue_date.isoformat(),
            "due_date": due_date.isoformat(),
            "paid": int(paid_flag),
        }

    # Distribute each segment across cities so every filter has data.
    # Segment A: paid
    for i in range(paid_to_create):
        city = cities[i % len(cities)]
        tenant_id, rent = next_tenant_for_city(city)
        invoice_rows.append(make_invoice_row(tenant_id, rent, paid_flag=1, force_late=False))

    # Segment B: late unpaid (guaranteed overdue) - ALSO distributed across all cities
    for i in range(late_unpaid_to_create):
        city = cities[i % len(cities)]
        tenant_id, rent = next_tenant_for_city(city)
        invoice_rows.append(make_invoice_row(tenant_id, rent, paid_flag=0, force_late=True))

    # Segment C: upcoming unpaid
    remaining = invoices_to_create - paid_to_create - late_unpaid_to_create
    for i in range(remaining):
        city = cities[i % len(cities)]
        tenant_id, rent = next_tenant_for_city(city)
        invoice_rows.append(make_invoice_row(tenant_id, rent, paid_flag=0, force_late=False))

    # Safety: keep deterministic length
    invoice_rows = invoice_rows[:invoices_to_create]

    inserted_invoice_ids = []
    for idx, row in enumerate(invoice_rows):
        cur.execute(
            """
            INSERT INTO invoices (tenant_ID, amount_due, due_date, issue_date, paid)
            VALUES (?, ?, ?, ?, ?)
            """,
            (row["tenant_id"], row["amount_due"], row["due_date"], row["issue_date"], row["paid"]),
        )
        inserted_invoice_ids.append(int(cur.lastrowid))

    # Create payments for the paid invoices
    for idx in range(paid_to_create):
        invoice_id = inserted_invoice_ids[idx]
        inv = invoice_rows[idx]
        payment_date = date.fromisoformat(inv["issue_date"]) + timedelta(days=random.randint(0, 10))

        cur.execute(
            """
            INSERT INTO payments (invoice_ID, tenant_ID, payment_date, amount)
            VALUES (?, ?, ?, ?)
            """,
            (invoice_id, inv["tenant_id"], payment_date.isoformat(), inv["amount_due"]),
        )

    conn.commit()

    counts = {
        "invoices": _table_row_count(conn, "invoices"),
        "payments": _table_row_count(conn, "payments"),
    }
    conn.close()
    inserted = {
        "invoices": counts["invoices"] - (0 if reset else before_counts["invoices"]),
        "payments": counts["payments"] - (0 if reset else before_counts["payments"]),
    }
    return counts, inserted


def main():
    parser = argparse.ArgumentParser(description="Seed finance test data into the SQLite DB.")
    parser.add_argument("--invoices", type=int, default=50, help="Number of invoices to insert (default: 50)")
    parser.add_argument("--paid", type=int, default=30, help="Number of invoices to mark paid (also inserts payments) (default: 30)")
    parser.add_argument("--late-unpaid", type=int, default=15, help="Number of invoices to create as unpaid AND overdue (default: 15)")
    parser.add_argument("--reset", action="store_true", help="Delete existing invoices/payments before seeding")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    counts, inserted = seed_finance_data(
        invoices_to_create=args.invoices,
        paid_to_create=args.paid,
        late_unpaid_to_create=args.late_unpaid,
        reset=args.reset,
        seed=args.seed,
    )

    print(f"OK: Finance test data seeded into: {DB_PATH}")
    if not args.reset:
        print(f"Inserted this run -> Invoices: {inserted['invoices']} | Payments: {inserted['payments']}")
    print(f"Invoices: {counts['invoices']}")
    print(f"Payments: {counts['payments']}")


if __name__ == "__main__":
    main()


"""
Seed Test Data (Finance + Maintenance)

This tool inserts test data into the existing SQLite database:
  - invoices (80 by default) - distributed across ALL cities (Bristol, Cardiff, London, Manchester)
  - payments for a subset of invoices (50 by default), also marks those invoices as paid
  - GUARANTEES a subset of invoices are unpaid AND overdue (late) for UI testing
  - Invoices spread over 12 months so Finance/Manager trend charts show meaningful data per city
  - maintenance requests (20 by default) with varying statuses and priorities

It is designed to support Finance Manager and Manager UI testing across all locations.

Usage:
  python setupfiles/tools/seed_testdata.py --reset --invoices 80 --paid 50 --late-unpaid 20
  python setupfiles/tools/seed_testdata.py --invoices 80 --paid 50
  python setupfiles/tools/seed_testdata.py --maintenance 20 --completed 10
  python setupfiles/tools/seed_testdata.py --reset --invoices 80 --maintenance 20
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


def _fetch_apartments_with_tenants(conn):
    """
    Returns a list of dicts with apartment_id, tenant_id, city for active leases.
    Used for maintenance request seeding.
    """
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            a.apartment_ID AS apartment_id,
            la.tenant_ID AS tenant_id,
            l.city AS city
        FROM lease_agreements la
        JOIN apartments a ON la.apartment_ID = a.apartment_ID
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE la.active = 1
        ORDER BY l.city, a.apartment_ID
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

    # Build month slots so each city gets invoices spread across all months (avoids zeros)
    month_slots = []
    y, m = today.year, today.month
    for _ in range(12):
        m -= 1
        if m == 0:
            m, y = 12, y - 1
        month_slots.append(date(y, m, 1))
    month_slots = list(reversed(month_slots))  # oldest first

    def make_invoice_row(tenant_id: int, rent: float, paid_flag: int, force_late: bool, slot_idx: int = 0):
        if paid_flag == 1:
            # Paid: spread evenly across months so no month has zero
            base = month_slots[slot_idx % len(month_slots)]
            day_offset = random.randint(0, min(27, (today - base).days)) if base < today else 0
            issue_date = base + timedelta(days=day_offset)
            due_date = issue_date + timedelta(days=random.choice([7, 14, 21, 28]))
        elif force_late:
            # Late unpaid: spread across months, due_date before today
            base = month_slots[slot_idx % len(month_slots)]
            if base >= today:
                base = today - timedelta(days=90)
            day_offset = random.randint(0, min(27, (today - base).days)) if base < today else 0
            issue_date = base + timedelta(days=day_offset)
            due_date = today - timedelta(days=random.randint(1, 45))
            if due_date <= issue_date:
                issue_date = due_date - timedelta(days=random.randint(7, 28))
        else:
            # Upcoming unpaid: spread across months, due in future
            base = month_slots[slot_idx % len(month_slots)]
            if base > today:
                base = today - timedelta(days=30)
            day_offset = random.randint(0, min(27, (today - base).days)) if base < today else 0
            issue_date = base + timedelta(days=day_offset)
            due_date = today + timedelta(days=random.randint(1, 60))

        amount_due = max(50.0, round(rent + random.uniform(-30, 80), 2))
        return {
            "tenant_id": int(tenant_id),
            "amount_due": float(amount_due),
            "issue_date": issue_date.isoformat(),
            "due_date": due_date.isoformat(),
            "paid": int(paid_flag),
        }

    # Distribute each segment across ALL cities so every city gets data in every month.
    # Segment A: paid invoices - spread across months so no zero months in trend charts
    for i in range(paid_to_create):
        city = cities[i % len(cities)]
        tenant_id, rent = next_tenant_for_city(city)
        invoice_rows.append(make_invoice_row(tenant_id, rent, paid_flag=1, force_late=False, slot_idx=i))

    # Segment B: late unpaid - spread across months
    for i in range(late_unpaid_to_create):
        city = cities[i % len(cities)]
        tenant_id, rent = next_tenant_for_city(city)
        invoice_rows.append(make_invoice_row(tenant_id, rent, paid_flag=0, force_late=True, slot_idx=i))

    # Segment C: upcoming unpaid - spread across months
    remaining = invoices_to_create - paid_to_create - late_unpaid_to_create
    for i in range(remaining):
        city = cities[i % len(cities)]
        tenant_id, rent = next_tenant_for_city(city)
        invoice_rows.append(make_invoice_row(tenant_id, rent, paid_flag=0, force_late=False, slot_idx=i))

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


def seed_maintenance_data(
    requests_to_create: int = 20,
    completed_to_create: int = 10,
    reset: bool = False,
    seed: int = 42,
):
    """
    Seed maintenance requests into the DB.

    Args:
        requests_to_create: number of maintenance request rows to insert
        completed_to_create: number of requests that will be marked as completed
        reset: if True, deletes existing maintenance requests first
        seed: random seed for repeatable data
    """
    random.seed(seed)

    # Sample maintenance issues
    ISSUES = [
        "Leaking faucet in bathroom",
        "Broken dishwasher - not draining",
        "Air conditioning not working",
        "Heating system malfunction",
        "Clogged toilet",
        "Broken window lock",
        "Faulty electrical outlet in bedroom",
        "Refrigerator making loud noise",
        "Water heater not producing hot water",
        "Damaged flooring in living room",
        "Leaking pipe under sink",
        "Smoke detector beeping continuously",
        "Oven not heating properly",
        "Door lock jammed",
        "Shower drain clogged",
        "Light fixture flickering",
        "Garbage disposal not working",
        "Thermostat not responding",
        "Water pressure issues",
        "Ceiling stain - possible leak",
        "Broken cabinet hinge",
        "Washing machine leaking",
        "Mold in bathroom",
        "Pest control needed - rodents",
        "Balcony door won't close properly",
    ]

    conn = _connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    before_count = _table_row_count(conn, "maintenance_requests")

    if reset:
        cur.execute("DELETE FROM maintenance_requests")
        conn.commit()

    apartments = _fetch_apartments_with_tenants(conn)
    if not apartments:
        raise RuntimeError("No active leases found; cannot create maintenance requests.")

    # Normalize counts
    requests_to_create = int(max(0, requests_to_create))
    completed_to_create = int(max(0, min(completed_to_create, requests_to_create)))

    today = date.today()
    request_rows = []

    # Helper to create a maintenance request
    def make_request_row(apartment_id: int, tenant_id: int, is_completed: bool):
        issue = random.choice(ISSUES)
        priority = random.randint(1, 5)  # 1=low, 5=urgent
        
        # Reported date: within last 90 days
        reported_offset = random.randint(0, 90)
        reported_date = today - timedelta(days=reported_offset)
        
        # Scheduled date logic
        if is_completed:
            # Completed requests had scheduled dates in the past
            scheduled_offset = random.randint(1, reported_offset) if reported_offset > 0 else 0
            scheduled_date = today - timedelta(days=scheduled_offset)
        else:
            # Pending requests: some scheduled in the future, some not scheduled yet
            if random.random() < 0.6:  # 60% have scheduled dates
                scheduled_date = today + timedelta(days=random.randint(1, 30))
            else:
                scheduled_date = None
        
        # Cost: completed ones have costs, pending high-priority might have estimates
        if is_completed:
            cost = round(random.uniform(50, 800), 2)
        elif priority >= 4 and random.random() < 0.5:
            cost = round(random.uniform(100, 600), 2)  # Estimated cost
        else:
            cost = None
        
        return {
            "apartment_id": int(apartment_id),
            "tenant_id": int(tenant_id),
            "issue_description": issue,
            "priority_level": int(priority),
            "reported_date": reported_date.isoformat(),
            "scheduled_date": scheduled_date.isoformat() if scheduled_date else None,
            "completed": 1 if is_completed else 0,
            "cost": cost,
        }

    # Create completed requests
    for i in range(completed_to_create):
        apt = apartments[i % len(apartments)]
        request_rows.append(make_request_row(apt["apartment_id"], apt["tenant_id"], is_completed=True))

    # Create pending requests
    for i in range(requests_to_create - completed_to_create):
        apt = apartments[(i + completed_to_create) % len(apartments)]
        request_rows.append(make_request_row(apt["apartment_id"], apt["tenant_id"], is_completed=False))

    # Safety: keep deterministic length
    request_rows = request_rows[:requests_to_create]

    # Insert all requests
    for row in request_rows:
        cur.execute(
            """
            INSERT INTO maintenance_requests 
            (apartment_ID, tenant_ID, issue_description, priority_level, 
             reported_date, scheduled_date, completed, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["apartment_id"],
                row["tenant_id"],
                row["issue_description"],
                row["priority_level"],
                row["reported_date"],
                row["scheduled_date"],
                row["completed"],
                row["cost"],
            ),
        )

    conn.commit()

    after_count = _table_row_count(conn, "maintenance_requests")
    conn.close()

    inserted = after_count - (0 if reset else before_count)
    return {"total": after_count, "inserted": inserted}


def main():
    parser = argparse.ArgumentParser(description="Seed finance and maintenance test data into the SQLite DB.")
    # Finance arguments
    parser.add_argument("--invoices", type=int, default=80, help="Number of invoices to insert across all cities (default: 80)")
    parser.add_argument("--paid", type=int, default=50, help="Number of invoices to mark paid (also inserts payments) (default: 50)")
    parser.add_argument("--late-unpaid", type=int, default=20, help="Number of invoices to create as unpaid AND overdue (default: 20)")
    # Maintenance arguments
    parser.add_argument("--maintenance", type=int, default=20, help="Number of maintenance requests to insert (default: 20)")
    parser.add_argument("--completed", type=int, default=10, help="Number of maintenance requests to mark completed (default: 10)")
    # Common arguments
    parser.add_argument("--reset", action="store_true", help="Delete existing invoices/payments/maintenance requests before seeding")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--finance-only", action="store_true", help="Seed only finance data")
    parser.add_argument("--maintenance-only", action="store_true", help="Seed only maintenance data")
    args = parser.parse_args()

    seed_finance = not args.maintenance_only
    seed_maintenance = not args.finance_only

    finance_counts = None
    finance_inserted = None
    maintenance_stats = None

    if seed_finance:
        finance_counts, finance_inserted = seed_finance_data(
            invoices_to_create=args.invoices,
            paid_to_create=args.paid,
            late_unpaid_to_create=args.late_unpaid,
            reset=args.reset,
            seed=args.seed,
        )

    if seed_maintenance:
        maintenance_stats = seed_maintenance_data(
            requests_to_create=args.maintenance,
            completed_to_create=args.completed,
            reset=args.reset,
            seed=args.seed,
        )

    print(f"OK: Test data seeded into: {DB_PATH}")
    print()
    
    if finance_counts:
        if not args.reset:
            print(f"Finance - Inserted this run -> Invoices: {finance_inserted['invoices']} | Payments: {finance_inserted['payments']}")
        print(f"Finance - Total Invoices: {finance_counts['invoices']}")
        print(f"Finance - Total Payments: {finance_counts['payments']}")
        
    if maintenance_stats:
        if not args.reset:
            print(f"Maintenance - Inserted this run: {maintenance_stats['inserted']}")
        print(f"Maintenance - Total Requests: {maintenance_stats['total']}")


if __name__ == "__main__":
    main()


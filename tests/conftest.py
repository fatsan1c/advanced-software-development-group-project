import sys
from pathlib import Path

import os
import sqlite3

import pytest


def pytest_sessionstart(session):
    """
    Ensure the app's non-package imports work when tests are executed from repo root.

    The codebase uses imports like `import database_operations...` (not
    `paragonapartments.database_operations...`), so we add `paragonapartments/`
    to sys.path for the duration of the test session.
    """
    repo_root = Path(__file__).resolve().parents[1]
    app_root = repo_root / "paragonapartments"
    sys.path.insert(0, str(app_root))


def _create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # Core tables used across repositories
    cur.execute("""
        CREATE TABLE locations (
            location_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT UNIQUE,
            address TEXT UNIQUE
        )
        """)
    cur.execute("""
        CREATE TABLE apartments (
            apartment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            location_ID INTEGER,
            apartment_address TEXT,
            number_of_beds INTEGER,
            monthly_rent REAL,
            occupied INTEGER DEFAULT 0,
            FOREIGN KEY (location_ID) REFERENCES locations(location_ID)
        )
        """)
    cur.execute("""
        CREATE TABLE tenants (
            tenant_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            NI_number TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            occupation TEXT,
            annual_salary REAL,
            pets TEXT DEFAULT 'N',
            right_to_rent TEXT DEFAULT 'N',
            credit_check TEXT DEFAULT 'Pending'
        )
        """)
    cur.execute("""
        CREATE TABLE lease_agreements (
            lease_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_ID INTEGER,
            apartment_ID INTEGER,
            start_date TEXT,
            end_date TEXT,
            monthly_rent REAL,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (tenant_ID) REFERENCES tenants(tenant_ID),
            FOREIGN KEY (apartment_ID) REFERENCES apartments(apartment_ID)
        )
        """)
    cur.execute("""
        CREATE TABLE users (
            user_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            location_ID INTEGER,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT,
            FOREIGN KEY (location_ID) REFERENCES locations(location_ID)
        )
        """)
    cur.execute("""
        CREATE TABLE invoices (
            invoice_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_ID INTEGER,
            amount_due REAL,
            due_date TEXT,
            issue_date TEXT,
            paid INTEGER DEFAULT 0,
            FOREIGN KEY (tenant_ID) REFERENCES tenants(tenant_ID)
        )
        """)
    cur.execute("""
        CREATE TABLE payments (
            payment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_ID INTEGER,
            tenant_ID INTEGER,
            payment_date TEXT,
            amount REAL,
            FOREIGN KEY (invoice_ID) REFERENCES invoices(invoice_ID),
            FOREIGN KEY (tenant_ID) REFERENCES tenants(tenant_ID)
        )
        """)
    cur.execute("""
        CREATE TABLE complaint (
            complaint_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_ID INTEGER,
            description TEXT,
            date_submitted TEXT,
            resolved INTEGER DEFAULT 0,
            FOREIGN KEY (tenant_ID) REFERENCES tenants(tenant_ID)
        )
        """)
    cur.execute("""
        CREATE TABLE maintenance_requests (
            request_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            apartment_ID INTEGER,
            tenant_ID INTEGER,
            issue_description TEXT,
            priority_level INTEGER,
            reported_date TEXT,
            scheduled_date TEXT,
            completed INTEGER DEFAULT 0,
            cost REAL,
            FOREIGN KEY (apartment_ID) REFERENCES apartments(apartment_ID),
            FOREIGN KEY (tenant_ID) REFERENCES tenants(tenant_ID)
        )
        """)

    # Useful indexes (keep tests fast when data grows)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_invoices_tenant ON invoices(tenant_ID)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_invoices_paid_due ON invoices(paid, due_date)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_ID)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_lease_tenant_active ON lease_agreements(tenant_ID, active)"
    )
    conn.commit()


def _seed_minimal_data(conn: sqlite3.Connection) -> dict:
    """
    Insert a minimal, consistent dataset used by integration tests.
    Returns IDs for convenience.
    """
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # Locations
    cur.execute(
        "INSERT INTO locations (city, address) VALUES (?, ?)",
        ("Bristol", "1 Test St, Bristol"),
    )
    bristol_id = int(cur.lastrowid)
    cur.execute(
        "INSERT INTO locations (city, address) VALUES (?, ?)",
        ("Cardiff", "2 Test St, Cardiff"),
    )
    cardiff_id = int(cur.lastrowid)

    # Apartments
    cur.execute(
        """
        INSERT INTO apartments (location_ID, apartment_address, number_of_beds, monthly_rent, occupied)
        VALUES (?, ?, ?, ?, ?)
        """,
        (bristol_id, "Flat 1", 1, 900.0, 1),
    )
    apt1_id = int(cur.lastrowid)
    cur.execute(
        """
        INSERT INTO apartments (location_ID, apartment_address, number_of_beds, monthly_rent, occupied)
        VALUES (?, ?, ?, ?, ?)
        """,
        (cardiff_id, "Flat 2", 2, 1100.0, 1),
    )
    apt2_id = int(cur.lastrowid)

    # Tenants
    cur.execute(
        """
        INSERT INTO tenants (
            first_name, last_name, date_of_birth, NI_number, email, phone,
            occupation, annual_salary, pets, right_to_rent, credit_check
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Alice",
            "Tenant",
            "1990-01-01",
            "AB123456A",
            "alice@example.com",
            "07123456789",
            "Engineer",
            50000,
            "N",
            "Y",
            "Passed",
        ),
    )
    tenant1_id = int(cur.lastrowid)
    cur.execute(
        """
        INSERT INTO tenants (
            first_name, last_name, date_of_birth, NI_number, email, phone,
            occupation, annual_salary, pets, right_to_rent, credit_check
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Bob",
            "Tenant",
            "1985-05-05",
            "AC123456B",
            "bob@example.com",
            "07987654321",
            "Teacher",
            42000,
            "Y",
            "Y",
            "Pending",
        ),
    )
    tenant2_id = int(cur.lastrowid)

    # Active leases (finance joins infer city via active lease)
    cur.execute(
        """
        INSERT INTO lease_agreements (tenant_ID, apartment_ID, start_date, end_date, monthly_rent, active)
        VALUES (?, ?, ?, ?, ?, 1)
        """,
        (tenant1_id, apt1_id, "2025-01-01", "2026-01-01", 900.0),
    )
    lease1_id = int(cur.lastrowid)
    cur.execute(
        """
        INSERT INTO lease_agreements (tenant_ID, apartment_ID, start_date, end_date, monthly_rent, active)
        VALUES (?, ?, ?, ?, ?, 1)
        """,
        (tenant2_id, apt2_id, "2025-02-01", "2026-02-01", 1100.0),
    )
    lease2_id = int(cur.lastrowid)

    # One unpaid invoice + one paid invoice with payment
    cur.execute(
        """
        INSERT INTO invoices (tenant_ID, amount_due, due_date, issue_date, paid)
        VALUES (?, ?, ?, ?, 0)
        """,
        (tenant1_id, 100.0, "2025-12-01", "2025-11-01"),
    )
    unpaid_invoice_id = int(cur.lastrowid)
    cur.execute(
        """
        INSERT INTO invoices (tenant_ID, amount_due, due_date, issue_date, paid)
        VALUES (?, ?, ?, ?, 1)
        """,
        (tenant2_id, 200.0, "2025-10-01", "2025-09-01"),
    )
    paid_invoice_id = int(cur.lastrowid)
    cur.execute(
        """
        INSERT INTO payments (invoice_ID, tenant_ID, payment_date, amount)
        VALUES (?, ?, ?, ?)
        """,
        (paid_invoice_id, tenant2_id, "2025-09-15", 200.0),
    )
    payment_id = int(cur.lastrowid)

    conn.commit()
    return {
        "locations": {"bristol": bristol_id, "cardiff": cardiff_id},
        "apartments": {"apt1": apt1_id, "apt2": apt2_id},
        "tenants": {"alice": tenant1_id, "bob": tenant2_id},
        "leases": {"lease1": lease1_id, "lease2": lease2_id},
        "invoices": {"unpaid": unpaid_invoice_id, "paid": paid_invoice_id},
        "payments": {"payment": payment_id},
    }


@pytest.fixture()
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture()
def set_test_db_env(monkeypatch: pytest.MonkeyPatch, temp_db_path: Path) -> Path:
    monkeypatch.setenv("PAMS_DB_PATH", str(temp_db_path))
    return temp_db_path


@pytest.fixture()
def init_schema(set_test_db_env: Path) -> Path:
    # Create DB file + schema
    conn = sqlite3.connect(str(set_test_db_env))
    try:
        _create_schema(conn)
    finally:
        conn.close()
    return set_test_db_env


@pytest.fixture()
def seed_minimal_data(init_schema: Path) -> dict:
    conn = sqlite3.connect(str(init_schema))
    try:
        conn.row_factory = sqlite3.Row
        return _seed_minimal_data(conn)
    finally:
        conn.close()

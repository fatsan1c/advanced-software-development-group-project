"""
Creates SQLite database with test data.
"""

import sqlite3
import os
from passlib.hash import sha256_crypt

# Path to the SQLite database file (will be stored in the database folder)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'paragonapartments', 'database', 'paragonapartments.db')

def create_database():
    """Create SQLite database with schema and data."""
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    print("Creating tables...")
    
    # Create locations table
    cursor.execute("""
    CREATE TABLE locations (
        location_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT UNIQUE,
        address TEXT UNIQUE
    )
    """)
    
    # Create apartments table
    cursor.execute("""
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
    
    # Create tenants table
    cursor.execute("""
    CREATE TABLE tenants (
        tenant_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        NI_number TEXT,
        email TEXT,
        phone TEXT
    )
    """)
    
    # Create lease_agreements table
    cursor.execute("""
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
    
    # Create users table
    cursor.execute("""
    CREATE TABLE users (
        user_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        location_ID INTEGER,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT,
        FOREIGN KEY (location_ID) REFERENCES locations(location_ID)
    )
    """)
    
    # Create invoices table
    cursor.execute("""
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
    
    # Create payments table
    cursor.execute("""
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
    
    # Create complaint table
    cursor.execute("""
    CREATE TABLE complaint (
        complaint_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_ID INTEGER,
        description TEXT,
        date_submitted TEXT,
        resolved INTEGER DEFAULT 0,
        FOREIGN KEY (tenant_ID) REFERENCES tenants(tenant_ID)
    )
    """)
    
    # Create maintenance_requests table
    cursor.execute("""
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

    print("Inserting data...")
    
    # Insert locations
    cursor.executemany("INSERT INTO locations (location_ID, city, address) VALUES (?, ?, ?)", [
        (1, 'Bristol', '12 Broadmead, Bristol, BS2 ZPK'),
        (2, 'Cardiff', '15 Tredegar St, Cardiff, CF5Z 6GP'),
        (3, 'London', '18 Rupert St, London, EC1A 6IQ'),
        (4, 'Manchester', '23 Corporation St, Manchester, M3T 3AM')
    ])

    # Insert users (with hashed password)
    users_data = [
        (1,None,'manager',sha256_crypt.hash('paragon1'),'manager')
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", users_data)
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ SQLite database created successfully at: {DB_PATH}")
    print(f"Database size: {os.path.getsize(DB_PATH) / 1024:.2f} KB")

if __name__ == "__main__":
    create_database()

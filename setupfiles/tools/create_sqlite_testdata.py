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
    
    # Insert apartments
    apartments_data = [
        (1,1,'Apartment 1',1,850,1), (2,1,'Apartment 2',2,1050,1), (3,1,'Apartment 3',3,1350,1),
        (4,1,'Apartment 4',2,1100,1), (5,1,'Apartment 5',1,900,1), (6,1,'Apartment 6',2,1000,1),
        (7,1,'Apartment 7',1,820,0), (8,1,'Apartment 8',3,1400,0), (9,2,'Apartment 1',1,700,1),
        (10,2,'Apartment 2',2,850,1), (11,2,'Apartment 3',3,1100,1), (12,2,'Apartment 4',2,900,1),
        (13,2,'Apartment 5',1,750,1), (14,2,'Apartment 6',2,830,0), (15,2,'Apartment 7',1,680,0),
        (16,2,'Apartment 8',3,1150,0), (17,3,'Apartment 1',1,1300,1), (18,3,'Apartment 2',2,1700,1),
        (19,3,'Apartment 3',3,2200,1), (20,3,'Apartment 4',2,1800,1), (21,3,'Apartment 5',1,1400,1),
        (22,3,'Apartment 6',2,1650,0), (23,3,'Apartment 7',1,1250,0), (24,3,'Apartment 8',3,2300,0),
        (25,4,'Apartment 1',1,800,1), (26,4,'Apartment 2',2,950,1), (27,4,'Apartment 3',3,1200,1),
        (28,4,'Apartment 4',2,1000,1), (29,4,'Apartment 5',1,850,1), (30,4,'Apartment 6',2,920,0),
        (31,4,'Apartment 7',1,780,0), (32,4,'Apartment 8',3,1250,0)
    ]
    cursor.executemany("INSERT INTO apartments VALUES (?, ?, ?, ?, ?, ?)", apartments_data)
    
    # Insert tenants with realistic UK data
    tenants_data = [
        (1,'Alice','Brown','1992-03-15','AB123456C','alice.brown@demo.com','07111111111','Software Engineer',45000,'N','Y','Passed'),
        (2,'James','Wilson','1988-07-22','JW234567A','james.wilson@demo.com','07111111112','Accountant',38000,'N','Y','Passed'),
        (3,'Emily','Carter','1995-11-08','EC345678B','emily.carter@demo.com','07111111113','Nurse',32000,'Y','Y','Passed'),
        (4,'Michael','Green','1990-01-30','MG456789D','michael.green@demo.com','07111111114','Teacher',35000,'N','Y','Passed'),
        (5,'Sophie','Taylor','1993-05-14','ST567890C','sophie.taylor@demo.com','07111111115','Marketing Manager',42000,'Y','Y','Passed'),
        (6,'Daniel','Harris','1991-09-18','DH678901A','daniel.harris@demo.com','07222222221','Chef',28000,'N','Y','Passed'),
        (7,'Olivia','Martin','1994-12-03','OM789012B','olivia.martin@demo.com','07222222222','Graphic Designer',36000,'Y','Y','Passed'),
        (8,'Thomas','Lewis','1987-06-25','TL890123D','thomas.lewis@demo.com','07222222223','Engineer',48000,'N','Y','Passed'),
        (9,'Lucy','Walker','1996-02-11','LW901234A','lucy.walker@demo.com','07222222224','Pharmacist',40000,'N','Y','Passed'),
        (10,'Ben','Scott','1989-08-07','BS012345C','ben.scott@demo.com','07222222225','Sales Executive',33000,'N','Y','Passed'),
        (11,'Harry','King','1985-04-19','HK112233B','harry.king@demo.com','07333333331','Lawyer',65000,'N','Y','Passed'),
        (12,'Amelia','Wright','1992-10-27','AW223344D','amelia.wright@demo.com','07333333332','Doctor',72000,'N','Y','Passed'),
        (13,'Jack','Turner','1990-07-13','JT334455A','jack.turner@demo.com','07333333333','Financial Analyst',58000,'N','Y','Passed'),
        (14,'Isla','Patel','1993-01-05','IP445566C','isla.patel@demo.com','07333333334','Architect',52000,'Y','Y','Passed'),
        (15,'Noah','Ahmed','1988-11-21','NA556677B','noah.ahmed@demo.com','07333333335','Consultant',61000,'N','Y','Passed'),
        (16,'Liam','ONeill','1991-05-08','LO667788D','liam.oneill@demo.com','07444444441','Electrician',31000,'N','Y','Passed'),
        (17,'Mia','Roberts','1994-09-16','MR778899A','mia.roberts@demo.com','07444444442','Veterinarian',38000,'Y','Y','Passed'),
        (18,'Ethan','Wood','1986-12-29','EW889900C','ethan.wood@demo.com','07444444443','Project Manager',47000,'N','Y','Passed'),
        (19,'Grace','Hall','1995-03-22','GH990011B','grace.hall@demo.com','07444444444','Social Worker',29000,'N','Y','Passed'),
        (20,'Oliver','Price','1992-08-14','OP001122D','oliver.price@demo.com','07444444445','IT Support',34000,'Y','Y','Passed'),
        (21,'Alice','Smith','1997-03-15','AS143456P','alice.smith@demo.com','07111111112','Professor',65000,'N','Y','Passed')
    ]
    cursor.executemany("INSERT INTO tenants VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tenants_data)
    
    # Insert lease_agreements
    leases_data = [
        (1,1,1,'2024-01-01','2025-01-01',850,1), (2,2,2,'2024-02-01','2025-02-01',750,1),
        (3,3,3,'2024-03-01','2025-03-01',1100,1), (4,4,4,'2024-01-15','2025-01-15',900,1),
        (5,5,5,'2024-04-01','2025-04-01',700,1), (6,6,9,'2024-02-01','2025-02-01',780,1),
        (7,7,10,'2024-03-01','2025-03-01',680,1), (8,8,11,'2024-01-01','2025-01-01',1000,1),
        (9,9,12,'2024-04-15','2025-04-15',820,1), (10,10,13,'2024-05-01','2025-05-01',650,1),
        (11,11,17,'2024-01-01','2025-01-01',1500,1), (12,12,18,'2024-02-01','2025-02-01',1300,1),
        (13,13,19,'2024-03-01','2025-03-01',2000,1), (14,14,20,'2024-04-01','2025-04-01',1700,1),
        (15,15,21,'2024-05-01','2025-05-01',1200,1), (16,16,25,'2024-01-01','2025-01-01',900,1),
        (17,17,26,'2024-02-01','2025-02-01',780,1), (18,18,27,'2024-03-01','2025-03-01',1150,1),
        (19,19,28,'2024-04-01','2025-04-01',950,1), (20,20,29,'2024-05-01','2025-05-01',720,1),
        (21,21,6,'2024-06-01','2025-06-01',950,1)
    ]
    cursor.executemany("INSERT INTO lease_agreements VALUES (?, ?, ?, ?, ?, ?, ?)", leases_data)
    
    # Insert users (with hashed passwords)
    users_data = [
        (1,None,'manager',sha256_crypt.hash('paragon1'),'manager'),
        (2,1,'bristol_admin',sha256_crypt.hash('admin1'),'admin'),
        (3,None,'finance',sha256_crypt.hash('finance1'),'finance'),
        (4,1,'bristol_frontdesk',sha256_crypt.hash('front1'),'frontdesk'),
        (5,1,'bristol_maintenance',sha256_crypt.hash('maint1'),'maintenance'),
        (7,2,'cardiff_admin',sha256_crypt.hash('admin1'),'admin'),
        (8,2,'cardiff_frontdesk',sha256_crypt.hash('front1'),'frontdesk'),
        (9,2,'cardiff_maintenance',sha256_crypt.hash('maint1'),'maintenance'),
        (10,3,'london_admin',sha256_crypt.hash('admin1'),'admin'),
        (11,3,'london_frontdesk',sha256_crypt.hash('front1'),'frontdesk'),
        (12,3,'london_maintenance',sha256_crypt.hash('maint1'),'maintenance'),
        (13,4,'manchester_admin',sha256_crypt.hash('admin1'),'admin'),
        (14,4,'manchester_frontdesk',sha256_crypt.hash('front1'),'frontdesk'),
        (15,4,'manchester_maintenance',sha256_crypt.hash('maint1'),'maintenance')
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", users_data)
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ SQLite database created successfully at: {DB_PATH}")
    print(f"Database size: {os.path.getsize(DB_PATH) / 1024:.2f} KB")

if __name__ == "__main__":
    create_database()

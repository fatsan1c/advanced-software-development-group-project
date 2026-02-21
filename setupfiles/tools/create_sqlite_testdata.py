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

    # Performance indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_tenant ON invoices(tenant_ID)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_paid_due ON invoices(paid, due_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_ID)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lease_tenant_active ON lease_agreements(tenant_ID, active)")
    
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
    
    # Insert apartments - location_ID: 1=Bristol, 2=Cardiff, 3=London, 4=Manchester
    # Vary occupied per city so stats differ: Bristol 6/8, Cardiff 5/8, London 8/8, Manchester 7/8
    apartments_data = [
        (1,1,'Apartment 1',1,850,1), (2,1,'Apartment 2',2,1050,1), (3,1,'Apartment 3',3,1350,1),
        (4,1,'Apartment 4',2,1100,1), (5,1,'Apartment 5',1,900,1), (6,1,'Apartment 6',2,1000,1),
        (7,1,'Apartment 7',1,820,1), (8,1,'Apartment 8',3,1400,0), (9,2,'Apartment 1',1,700,1),
        (10,2,'Apartment 2',2,850,1), (11,2,'Apartment 3',3,1100,0), (12,2,'Apartment 4',2,900,1),
        (13,2,'Apartment 5',1,750,1), (14,2,'Apartment 6',2,830,1), (15,2,'Apartment 7',1,680,0),
        (16,2,'Apartment 8',3,1150,0), (17,3,'Apartment 1',1,1300,1), (18,3,'Apartment 2',2,1700,1),
        (19,3,'Apartment 3',3,2200,1), (20,3,'Apartment 4',2,1800,1), (21,3,'Apartment 5',1,1400,1),
        (22,3,'Apartment 6',2,1650,1), (23,3,'Apartment 7',1,1250,1), (24,3,'Apartment 8',3,2300,1),
        (25,4,'Apartment 1',1,800,1), (26,4,'Apartment 2',2,950,1), (27,4,'Apartment 3',3,1200,1),
        (28,4,'Apartment 4',2,1000,1), (29,4,'Apartment 5',1,850,1), (30,4,'Apartment 6',2,920,1),
        (31,4,'Apartment 7',1,780,1), (32,4,'Apartment 8',3,1250,0)
    ]
    cursor.executemany("INSERT INTO apartments VALUES (?, ?, ?, ?, ?, ?)", apartments_data)
    
    # Insert tenants with realistic UK data (32 tenants for full occupancy)
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
        (21,'Emma','Cooper','1991-04-12','EC556677D','emma.cooper@demo.com','07555555551','Designer',37000,'N','Y','Passed'),
        (22,'William','Bennett','1989-11-03','WB667788E','william.bennett@demo.com','07555555552','Developer',52000,'N','Y','Passed'),
        (23,'Charlotte','Murphy','1994-07-19','CM778899F','charlotte.murphy@demo.com','07555555553','HR Manager',44000,'Y','Y','Passed'),
        (24,'Henry','Richardson','1987-02-28','HR889900G','henry.richardson@demo.com','07555555554','Analyst',46000,'N','Y','Passed'),
        (25,'Victoria','Cox','1992-09-14','VC990011H','victoria.cox@demo.com','07555555555','Writer',32000,'N','Y','Passed'),
        (26,'Samuel','Howard','1990-05-22','SH001122I','samuel.howard@demo.com','07555555556','Manager',55000,'N','Y','Passed'),
        (27,'Elizabeth','Ward','1993-12-08','EW112233J','elizabeth.ward@demo.com','07555555557','Consultant',48000,'Y','Y','Passed'),
        (28,'Joseph','Brooks','1988-08-17','JB223344K','joseph.brooks@demo.com','07555555558','Engineer',51000,'N','Y','Passed'),
        (29,'Hannah','Sanders','1995-01-25','HS334455L','hannah.sanders@demo.com','07555555559','Nurse',35000,'N','Y','Passed'),
        (30,'David','Reed','1986-06-30','DR445566M','david.reed@demo.com','07555555560','Teacher',38000,'N','Y','Passed'),
        (31,'Chloe','Bell','1991-10-11','CB556677N','chloe.bell@demo.com','07555555561','Marketing',41000,'Y','Y','Passed'),
        (32,'George','Bailey','1989-03-05','GB667788O','george.bailey@demo.com','07555555562','Accountant',45000,'N','Y','Passed'),
    ]
    cursor.executemany("INSERT INTO tenants VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tenants_data)
    
    # Insert lease_agreements - DIFFERENT per city so manager charts show distinct data
    # Bristol 6/8: early leases from 2022, growth then flat
    # Cardiff 5/8: fewer leases, later starts, different curve
    # London 8/8: premium rents, full since 2023
    # Manchester 7/8: gradual fill 2023-2024
    leases_data = [
        # Bristol (apts 1-6 only; 7,8 vacant)
        (1,1,1,'2022-06-01','2025-06-01',850,1), (2,2,2,'2022-09-01','2025-09-01',1050,1),
        (3,3,3,'2023-01-01','2025-12-31',1350,1), (4,4,4,'2023-04-01','2025-04-01',1100,1),
        (5,5,5,'2023-07-01','2025-07-01',900,1), (6,6,6,'2023-10-01','2026-10-01',1000,1),
        # Cardiff (apts 9,10,12,13,14 only; 11,15,16 vacant)
        (7,9,9,'2023-05-01','2025-05-01',700,1), (8,10,10,'2023-08-01','2025-08-01',850,1),
        (9,12,12,'2024-01-01','2026-01-01',900,1), (10,13,13,'2024-03-01','2026-03-01',750,1),
        (11,14,14,'2024-06-01','2026-06-01',830,1),
        # London (apts 17-24 all - premium, full since 2023)
        (12,17,17,'2023-01-01','2025-12-31',1300,1), (13,18,18,'2023-01-01','2025-12-31',1700,1),
        (14,19,19,'2023-01-01','2025-12-31',2200,1), (15,20,20,'2023-01-01','2025-12-31',1800,1),
        (16,21,21,'2023-01-01','2025-12-31',1400,1), (17,22,22,'2023-01-01','2025-12-31',1650,1),
        (18,23,23,'2023-01-01','2025-12-31',1250,1), (19,24,24,'2023-01-01','2025-12-31',2300,1),
        # Manchester (apts 25-31; 32 vacant)
        (20,25,25,'2023-03-01','2025-03-01',800,1), (21,26,26,'2023-06-01','2025-06-01',950,1),
        (22,27,27,'2023-09-01','2025-09-01',1200,1), (23,28,28,'2024-01-01','2026-01-01',1000,1),
        (24,29,29,'2024-04-01','2026-04-01',850,1), (25,30,30,'2024-07-01','2026-07-01',920,1),
        (26,31,31,'2024-10-01','2026-10-01',780,1),
    ]
    cursor.executemany("INSERT INTO lease_agreements VALUES (?, ?, ?, ?, ?, ?, ?)", leases_data)
    # Sync apartments.occupied from leases (1=has active lease, 0=vacant)
    cursor.execute("UPDATE apartments SET occupied = 0")
    cursor.execute("""
        UPDATE apartments SET occupied = 1 WHERE apartment_ID IN (
            SELECT DISTINCT apartment_ID FROM lease_agreements WHERE active = 1
        )
    """)
    
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
    
    print(f"\nSQLite database created successfully at: {DB_PATH}")
    print(f"Database size: {os.path.getsize(DB_PATH) / 1024:.2f} KB")

if __name__ == "__main__":
    create_database()

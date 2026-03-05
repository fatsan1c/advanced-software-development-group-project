"""
Generates comprehensive 10-year test data for Paragon Apartments.

Replaces any existing database with a full realistic UK dataset spanning
January 2015 through March 2026.

Tables populated:
  locations             :   4 rows
  apartments            : 100 rows (25 per city)
  tenants               : ~620 rows
  lease_agreements      : ~700+ rows
  users                 :  14 rows
  invoices              : ~14 000 rows  (monthly per active lease)
  payments              : ~12 500 rows  (most invoices paid; subset overdue)
  maintenance_requests  : ~3 000 rows
  complaint             : ~550 rows

Run with:
  python setupfiles/tools/create_sqlite_testdata.py
"""

from __future__ import annotations

import os
import random
import sqlite3
from datetime import date, timedelta
from passlib.hash import sha256_crypt

random.seed(42)

# ---------------------------------------------------------------------------
# Database path
# ---------------------------------------------------------------------------
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "paragonapartments",
    "database",
    "paragonapartments.db",
)

TODAY = date(2026, 3, 4)
START_DATE = date(2015, 1, 1)

# ---------------------------------------------------------------------------
# Name / demographic pools
# ---------------------------------------------------------------------------
MALE_FIRST = [
    "James", "Oliver", "Harry", "Jack", "George", "Noah", "Charlie", "Jacob",
    "Alfie", "Freddie", "Oscar", "William", "Thomas", "Joshua", "Ethan",
    "Muhammad", "Daniel", "Henry", "Samuel", "Joseph", "Dylan", "Logan",
    "Ryan", "Nathan", "Liam", "Adam", "Aaron", "Luke", "Benjamin", "Max",
    "Lewis", "Alex", "Callum", "Cameron", "Kieran", "Sean", "Ross", "Jamie",
    "Rory", "Connor", "Declan", "Brendan", "Patrick", "Niall", "Cian",
    "Mohammed", "Aiden", "Leon", "Marcus", "Reece",
]

FEMALE_FIRST = [
    "Olivia", "Amelia", "Isla", "Emily", "Ava", "Lily", "Sophia", "Mia",
    "Isabella", "Grace", "Freya", "Poppy", "Daisy", "Ella", "Evie",
    "Hannah", "Lucy", "Charlotte", "Alice", "Florence", "Millie", "Holly",
    "Jessica", "Sophie", "Ruby", "Chloe", "Ellie", "Molly", "Jasmine",
    "Imogen", "Zara", "Layla", "Fatima", "Ayesha", "Priya", "Anjali",
    "Niamh", "Saoirse", "Aoife", "Siobhan", "Orla", "Caoimhe", "Fiona",
    "Rhiannon", "Cerys", "Bethan", "Megan", "Sian", "Catrin", "Erin",
]

LAST_NAMES = [
    "Smith", "Jones", "Williams", "Taylor", "Brown", "Davies", "Evans",
    "Wilson", "Thomas", "Roberts", "Johnson", "Lewis", "Walker", "Robinson",
    "Wood", "Thompson", "White", "Watson", "Jackson", "Wright", "Green",
    "Harris", "Cooper", "King", "Lee", "Martin", "Clarke", "James", "Morgan",
    "Hughes", "Edwards", "Hill", "Scott", "Moore", "Ward", "Turner",
    "Carter", "Phillips", "Mitchell", "Patel", "Khan", "Ahmed", "Ali",
    "Singh", "Murray", "MacDonald", "Campbell", "Stewart", "Anderson",
    "Reid", "Morrison", "Fraser", "Gibson", "Grant", "Ross", "Kerr",
    "Flynn", "O'Brien", "Murphy", "Kelly", "O'Neill", "McCarthy",
    "Byrne", "Collins", "Walsh", "Ryan", "Sullivan", "Doyle",
    "Butler", "Fitzgerald", "Hayes", "Brennan", "Gallagher",
    "Sharma", "Gupta", "Rao", "Nair", "Iyer", "Mehta", "Desai",
    "Rogers", "Price", "Bennett", "Howard", "Barnes", "Cox", "Bailey",
    "Bell", "Gray", "Adams", "Brooks", "Reed", "Ford", "Lane", "Hall",
]

# (title, min_salary, max_salary)
OCCUPATIONS: list[tuple[str, int, int]] = [
    ("Software Engineer",      38000, 75000),
    ("Nurse",                  27000, 40000),
    ("Teacher",                28000, 48000),
    ("Accountant",             32000, 60000),
    ("Marketing Manager",      35000, 65000),
    ("Chef",                   22000, 38000),
    ("Graphic Designer",       25000, 45000),
    ("Civil Engineer",         35000, 65000),
    ("Pharmacist",             38000, 55000),
    ("Sales Executive",        24000, 45000),
    ("Lawyer",                 45000, 90000),
    ("Doctor",                 55000,100000),
    ("Financial Analyst",      40000, 75000),
    ("Architect",              38000, 70000),
    ("Consultant",             42000, 80000),
    ("Electrician",            28000, 48000),
    ("Veterinarian",           32000, 55000),
    ("Project Manager",        40000, 70000),
    ("Social Worker",          26000, 38000),
    ("IT Support",             26000, 42000),
    ("Data Analyst",           35000, 68000),
    ("HR Manager",             35000, 60000),
    ("Physiotherapist",        30000, 50000),
    ("Dentist",                55000, 95000),
    ("Police Officer",         26000, 45000),
    ("Delivery Driver",        21000, 30000),
    ("Retail Manager",         28000, 48000),
    ("University Lecturer",    38000, 65000),
    ("Barista",                19000, 24000),
    ("Plumber",                28000, 55000),
    ("Journalist",             26000, 50000),
    ("Solicitor",              40000, 85000),
    ("Paramedic",              28000, 42000),
    ("Estate Agent",           22000, 55000),
    ("Web Developer",          32000, 65000),
]

# (description, priority 1=low .. 5=critical)
MAINTENANCE_ISSUES: list[tuple[str, int]] = [
    ("Boiler not producing hot water", 4),
    ("Leaking tap in bathroom", 2),
    ("Broken window latch on bedroom", 3),
    ("Mould growth on bathroom ceiling", 3),
    ("Radiator not heating in living room", 3),
    ("Oven hob not igniting", 3),
    ("Blocked kitchen drain", 2),
    ("Faulty plug socket in bedroom", 3),
    ("Bathroom extractor fan not working", 2),
    ("Front door lock stiff and difficult to use", 3),
    ("Crack appearing in ceiling plaster", 2),
    ("Dishwasher not draining properly", 2),
    ("Washing machine drum making loud noise", 2),
    ("Toilet cistern running constantly", 2),
    ("Light fitting flickering in kitchen", 3),
    ("Communal hallway light bulb out", 1),
    ("Leak from upstairs apartment through ceiling", 5),
    ("Gas smell reported near cooker", 5),
    ("Window seal broken – draughty", 2),
    ("Pest sighting – mice in kitchen", 4),
    ("Smoke alarm beeping with low battery", 2),
    ("Intercom buzzer not working", 1),
    ("Shower pressure very low", 2),
    ("Damp patch on external-facing wall", 3),
    ("Broken kitchen cupboard hinge", 1),
    ("Heating system making clanking noise", 3),
    ("Fridge in apartment not cooling", 3),
    ("Water stain on bedroom ceiling", 3),
    ("Electric shower tripping the fuse board", 4),
    ("Condensation causing window frames to rot", 3),
]

COMPLAINT_DESCRIPTIONS: list[str] = [
    "Noise from upstairs neighbours late at night is persistent and disruptive.",
    "Rubbish left in communal hallway by other residents for several days.",
    "Parking space was occupied by an unknown vehicle on multiple occasions.",
    "Communal stairwell lighting has been out for over a week causing a safety hazard.",
    "Construction noise from neighbouring property starts before 7am daily.",
    "Package delivered to wrong apartment and not returned.",
    "There is a strong smell of damp in the communal entrance.",
    "Neighbours are smoking in the communal areas in breach of tenancy.",
    "The entry intercom has been broken for three weeks now.",
    "Bike stored in hallway is a fire obstruction risk.",
    "Water pressure drops completely every morning between 7am and 9am.",
    "Regular late-night parties in the flat above – excessive noise every weekend.",
    "Communal post box has been vandalised and is not secure.",
    "Lift has been out of service for two weeks and no update provided.",
    "Other residents are allowing their dogs to foul the communal garden.",
    "Broadband router in communal area was moved and internet access is intermittent.",
    "There is graffiti on the external wall that has not been cleaned.",
    "No hot water available on multiple occasions this month.",
    "Buzzer entry system allows entry without pressing any specific flat button.",
    "Window in communal stairwell is cracked and poses a safety risk.",
    "I was charged a late fee despite paying on time – please review.",
    "Maintenance team entered my apartment without 24 hours notice.",
    "Keys to the communal gym have not yet been provided after move-in.",
    "Recycling bins are overflowing and have not been collected this week.",
    "The emergency contact number provided does not connect to anyone.",
]

# ---------------------------------------------------------------------------
# Unique value generators
# ---------------------------------------------------------------------------
_used_ni: set[str] = set()
_used_emails: set[str] = set()

_NI_L1 = "ABCEGHJKLMNOPRSTWXYZ"
_NI_L2 = "ABCEGHJKLMNPRSTWXYZ"
_NI_SUFFIX = "ABCD"
_INVALID_PREFIXES = {"BG", "GB", "KN", "NK", "NT", "TN", "ZZ"}


def _gen_ni() -> str:
    for _ in range(200000):
        l1 = random.choice(_NI_L1)
        l2 = random.choice(_NI_L2)
        if f"{l1}{l2}" in _INVALID_PREFIXES:
            continue
        digits = f"{random.randint(0, 999999):06d}"
        suffix = random.choice(_NI_SUFFIX)
        ni = f"{l1}{l2}{digits}{suffix}"
        if ni not in _used_ni:
            _used_ni.add(ni)
            return ni
    raise RuntimeError("Could not generate unique NI number")


def _gen_email(first: str, last: str) -> str:
    base = f"{first.lower()}.{last.lower()}".replace("'", "").replace(" ", "")
    domains = [
        "gmail.com", "hotmail.co.uk", "outlook.com", "yahoo.co.uk",
        "icloud.com", "protonmail.com", "btinternet.com", "live.co.uk",
    ]
    for suffix in [""] + list(range(1, 9999)):
        candidate = f"{base}{suffix}@{random.choice(domains)}"
        if candidate not in _used_emails:
            _used_emails.add(candidate)
            return candidate
    raise RuntimeError("Could not generate unique email")


def _gen_phone() -> str:
    prefixes = [
        "07700", "07911", "07800", "07500", "07400",
        "07300", "07200", "07100", "07600", "07050",
    ]
    return f"{random.choice(prefixes)}{random.randint(100000, 999999)}"


def _random_dob() -> str:
    """Return a DOB for someone aged 21–65 at time of data generation."""
    year  = random.randint(1961, 2005)
    month = random.randint(1, 12)
    day   = random.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------
def _add_months(d: date, n: int) -> date:
    month = d.month - 1 + n
    year  = d.year + month // 12
    month = month % 12 + 1
    day   = min(d.day, 28)
    return date(year, month, day)


def _month_range(start: date, end: date):
    """Yield the first day of every calendar month in [start, end)."""
    cur  = date(start.year, start.month, 1)
    stop = date(end.year,   end.month,   1)
    while cur < stop:
        yield cur
        cur = _add_months(cur, 1)


# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------
SCHEMA_SQL = """
PRAGMA foreign_keys = OFF;

CREATE TABLE locations (
    location_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    city        TEXT UNIQUE,
    address     TEXT UNIQUE
);

CREATE TABLE apartments (
    apartment_ID      INTEGER PRIMARY KEY AUTOINCREMENT,
    location_ID       INTEGER,
    apartment_address TEXT,
    number_of_beds    INTEGER,
    monthly_rent      REAL,
    occupied          INTEGER DEFAULT 0,
    FOREIGN KEY (location_ID) REFERENCES locations(location_ID)
);

CREATE TABLE tenants (
    tenant_ID      INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name     TEXT NOT NULL,
    last_name      TEXT NOT NULL,
    date_of_birth  TEXT NOT NULL,
    NI_number      TEXT UNIQUE NOT NULL,
    email          TEXT UNIQUE NOT NULL,
    phone          TEXT NOT NULL,
    occupation     TEXT,
    annual_salary  REAL,
    pets           TEXT DEFAULT 'N',
    right_to_rent  TEXT DEFAULT 'N',
    credit_check   TEXT DEFAULT 'Pending'
);

CREATE TABLE lease_agreements (
    lease_ID     INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_ID    INTEGER,
    apartment_ID INTEGER,
    start_date   TEXT,
    end_date     TEXT,
    monthly_rent REAL,
    active       INTEGER DEFAULT 1,
    FOREIGN KEY (tenant_ID)    REFERENCES tenants(tenant_ID),
    FOREIGN KEY (apartment_ID) REFERENCES apartments(apartment_ID)
);

CREATE TABLE users (
    user_ID     INTEGER PRIMARY KEY AUTOINCREMENT,
    location_ID INTEGER,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,
    role        TEXT,
    FOREIGN KEY (location_ID) REFERENCES locations(location_ID)
);

CREATE TABLE invoices (
    invoice_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_ID  INTEGER,
    amount_due REAL,
    due_date   TEXT,
    issue_date TEXT,
    paid       INTEGER DEFAULT 0,
    FOREIGN KEY (tenant_ID) REFERENCES tenants(tenant_ID)
);

CREATE TABLE payments (
    payment_ID   INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_ID   INTEGER,
    payment_date TEXT,
    amount       REAL,
    FOREIGN KEY (invoice_ID) REFERENCES invoices(invoice_ID)
);

CREATE TABLE complaint (
    complaint_ID   INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_ID      INTEGER,
    description    TEXT,
    date_submitted TEXT,
    resolved       INTEGER DEFAULT 0,
    FOREIGN KEY (tenant_ID) REFERENCES tenants(tenant_ID)
);

CREATE TABLE maintenance_requests (
    request_ID        INTEGER PRIMARY KEY AUTOINCREMENT,
    apartment_ID      INTEGER,
    tenant_ID         INTEGER,
    issue_description TEXT,
    priority_level    INTEGER,
    reported_date     TEXT,
    scheduled_date    TEXT,
    completed         INTEGER DEFAULT 0,
    cost              REAL,
    FOREIGN KEY (apartment_ID) REFERENCES apartments(apartment_ID),
    FOREIGN KEY (tenant_ID)    REFERENCES tenants(tenant_ID)
);

CREATE INDEX IF NOT EXISTS idx_invoices_tenant     ON invoices(tenant_ID);
CREATE INDEX IF NOT EXISTS idx_invoices_paid_due   ON invoices(paid, due_date);
CREATE INDEX IF NOT EXISTS idx_payments_invoice    ON payments(invoice_ID);
CREATE INDEX IF NOT EXISTS idx_lease_tenant_active ON lease_agreements(tenant_ID, active);
CREATE INDEX IF NOT EXISTS idx_lease_apt_active    ON lease_agreements(apartment_ID, active);
CREATE INDEX IF NOT EXISTS idx_maint_apt           ON maintenance_requests(apartment_ID);
CREATE INDEX IF NOT EXISTS idx_complaint_tenant    ON complaint(tenant_ID);
"""

# ---------------------------------------------------------------------------
# Location & apartment definitions
# ---------------------------------------------------------------------------
LOCATIONS = [
    (1, "Bristol",    "12 Broadmead, Bristol, BS2 2PK"),
    (2, "Cardiff",    "15 Tredegar St, Cardiff, CF24 3GP"),
    (3, "London",     "18 Rupert St, London, EC1A 1IQ"),
    (4, "Manchester", "23 Corporation St, Manchester, M4 3AJ"),
]

# Base rents per city / bed count (2015 prices — inflated annually in data)
BASE_RENTS: dict[str, dict[int, int]] = {
    "Bristol":    {1: 750,  2: 950,  3: 1200},
    "Cardiff":    {1: 600,  2: 780,  3: 1000},
    "London":     {1: 1200, 2: 1600, 3: 2100},
    "Manchester": {1: 700,  2: 900,  3: 1150},
}

BLOCK_NAMES: dict[str, list[str]] = {
    "Bristol":    [
        "Clifton House", "Redcliffe Court", "Harbourside View",
        "Brandon Heights", "Temple Quay House",
    ],
    "Cardiff":    [
        "Bay View House", "Roath Court", "Canton Heights",
        "Pontcanna Place", "Cathays Court",
    ],
    "London":     [
        "Clerkenwell Tower", "Islington House", "Farringdon Gate",
        "Barbican Court", "Smithfield Place",
    ],
    "Manchester": [
        "Spinningfields House", "Northern Quarter Court", "Castlefield Gate",
        "Deansgate Heights", "Ancoats Court",
    ],
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def create_database() -> None:  # noqa: PLR0912, PLR0915
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # ---------------------------------------------------------------
    # 1. LOCATIONS
    # ---------------------------------------------------------------
    print("Inserting locations …")
    cur.executemany(
        "INSERT INTO locations (location_ID, city, address) VALUES (?, ?, ?)",
        LOCATIONS,
    )

    # ---------------------------------------------------------------
    # 2. APARTMENTS  (25 per city = 100 total)
    # ---------------------------------------------------------------
    print("Building apartments …")
    apartments_rows: list[tuple] = []
    apt_meta: dict[int, dict] = {}   # apt_id -> {location_id, city, beds, base_rent}
    apt_id_counter = 0

    for loc_id, city, _ in LOCATIONS:
        blocks = BLOCK_NAMES[city]
        # Bed-count distribution across 25 flats: ~8×1-bed, 12×2-bed, 5×3-bed
        beds_pool = [1]*8 + [2]*12 + [3]*5
        random.shuffle(beds_pool)
        flat_num = 1
        for i in range(25):
            apt_id_counter += 1
            block = blocks[i % len(blocks)]
            beds  = beds_pool[i]
            base  = BASE_RENTS[city][beds]
            # ±5% per-unit variation, rounded to nearest £5
            base  = round(base * random.uniform(0.95, 1.05) / 5) * 5
            addr  = f"Flat {flat_num}, {block}"
            flat_num += 1
            apartments_rows.append(
                (apt_id_counter, loc_id, addr, beds, float(base), 0)
            )
            apt_meta[apt_id_counter] = {
                "location_id": loc_id,
                "city":        city,
                "beds":        beds,
                "base_rent":   base,
            }

    cur.executemany(
        "INSERT INTO apartments "
        "(apartment_ID, location_ID, apartment_address, number_of_beds, monthly_rent, occupied) "
        "VALUES (?,?,?,?,?,?)",
        apartments_rows,
    )

    # ---------------------------------------------------------------
    # 3. TENANTS  (~620 unique UK tenants)
    # ---------------------------------------------------------------
    print("Generating tenants …")
    all_first = MALE_FIRST + FEMALE_FIRST
    tenant_pool: list[dict] = []
    for tid in range(1, 621):
        first = random.choice(all_first)
        last  = random.choice(LAST_NAMES)
        occ, sal_lo, sal_hi = random.choice(OCCUPATIONS)
        salary  = round(random.randint(sal_lo, sal_hi) / 500) * 500
        pets    = "Y" if random.random() < 0.22 else "N"
        r2r     = "Y" if random.random() < 0.93 else "N"
        credit  = (
            "Passed"  if random.random() < 0.87
            else ("Failed" if random.random() < 0.4 else "Pending")
        )
        tenant_pool.append({
            "id":         tid,
            "first":      first,
            "last":       last,
            "dob":        _random_dob(),
            "ni":         _gen_ni(),
            "email":      _gen_email(first, last),
            "phone":      _gen_phone(),
            "occupation": occ,
            "salary":     salary,
            "pets":       pets,
            "r2r":        r2r,
            "credit":     credit,
        })

    cur.executemany(
        "INSERT INTO tenants VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                t["id"], t["first"], t["last"], t["dob"],
                t["ni"], t["email"], t["phone"],
                t["occupation"], float(t["salary"]),
                t["pets"], t["r2r"], t["credit"],
            )
            for t in tenant_pool
        ],
    )

    # ---------------------------------------------------------------
    # 4. LEASE AGREEMENTS
    #    Simulate 11 years of occupancy per apartment (Jan 2015–Mar 2026).
    #    Tenants are drawn round-robin from the pool so each has ~1-2 leases.
    # ---------------------------------------------------------------
    print("Generating lease agreements …")

    def _inflated_rent(base: float, lease_start: date) -> float:
        """Apply ~3% annual rent inflation relative to 2015 baseline."""
        years = max(0, lease_start.year - 2015)
        return round(base * (1.03 ** years) / 5) * 5

    tenant_cycler = iter(tenant_pool)

    def _next_tenant() -> dict:
        nonlocal tenant_cycler
        try:
            return next(tenant_cycler)
        except StopIteration:
            shuffled = random.sample(tenant_pool, len(tenant_pool))
            tenant_cycler = iter(shuffled)
            return next(tenant_cycler)

    leases_rows: list[tuple] = []
    apt_active_lease: dict[int, dict] = {}   # apt_id -> last active lease info
    lease_id = 0

    # Stagger apartment availability: some blocks added later
    apt_ids_list = list(apt_meta.keys())
    random.shuffle(apt_ids_list)
    apt_open_offset: dict[int, int] = {
        aid: random.choice([0, 0, 0, 0, 3, 6, 12, 18, 0, 0])
        for aid in apt_ids_list
    }

    for apt_id_k in apt_ids_list:
        meta      = apt_meta[apt_id_k]
        base_rent = meta["base_rent"]
        cursor_dt = _add_months(START_DATE, apt_open_offset[apt_id_k])

        while cursor_dt <= TODAY:
            tenant   = _next_tenant()
            duration = random.choices(
                [6, 12, 18, 24],
                weights=[15, 55, 20, 10],
            )[0]
            l_start = cursor_dt
            l_end   = _add_months(l_start, duration)

            # Don't open a new lease if we're very close to TODAY
            if l_start > _add_months(TODAY, -4):
                break

            is_active = int(l_end > TODAY)
            rent = _inflated_rent(base_rent, l_start)

            lease_id += 1
            leases_rows.append((
                lease_id,
                tenant["id"],
                apt_id_k,
                l_start.isoformat(),
                l_end.isoformat(),
                float(rent),
                is_active,
            ))

            if is_active:
                apt_active_lease[apt_id_k] = {
                    "tenant_id": tenant["id"],
                    "rent":      rent,
                    "lease_id":  lease_id,
                    "start":     l_start,
                    "end":       l_end,
                }
                break  # No further leases once one is active

            # Gap between tenants: 1–3 months vacancy
            gap = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
            cursor_dt = _add_months(l_end, gap)

    cur.executemany(
        "INSERT INTO lease_agreements VALUES (?,?,?,?,?,?,?)",
        leases_rows,
    )

    # Mark apartments occupied based on active leases
    cur.execute("UPDATE apartments SET occupied = 0")
    cur.execute(
        """UPDATE apartments SET occupied = 1
           WHERE apartment_ID IN (
               SELECT DISTINCT apartment_ID FROM lease_agreements WHERE active = 1
           )"""
    )

    # ---------------------------------------------------------------
    # 5. USERS  (1 manager, 1 finance, 3 staff per city = 14 total)
    # ---------------------------------------------------------------
    print("Inserting users …")
    _pw = lambda s: sha256_crypt.hash(s)  # noqa: E731
    users_rows = [
        (1,  None, "manager",               _pw("paragon1"),  "manager"),
        (2,  None, "finance",               _pw("finance1"),  "finance"),
        (3,  1,    "bristol_admin",         _pw("admin1"),    "admin"),
        (4,  1,    "bristol_frontdesk",     _pw("front1"),    "frontdesk"),
        (5,  1,    "bristol_maintenance",   _pw("maint1"),    "maintenance"),
        (6,  2,    "cardiff_admin",         _pw("admin1"),    "admin"),
        (7,  2,    "cardiff_frontdesk",     _pw("front1"),    "frontdesk"),
        (8,  2,    "cardiff_maintenance",   _pw("maint1"),    "maintenance"),
        (9,  3,    "london_admin",          _pw("admin1"),    "admin"),
        (10, 3,    "london_frontdesk",      _pw("front1"),    "frontdesk"),
        (11, 3,    "london_maintenance",    _pw("maint1"),    "maintenance"),
        (12, 4,    "manchester_admin",      _pw("admin1"),    "admin"),
        (13, 4,    "manchester_frontdesk",  _pw("front1"),    "frontdesk"),
        (14, 4,    "manchester_maintenance",_pw("maint1"),    "maintenance"),
    ]
    cur.executemany("INSERT INTO users VALUES (?,?,?,?,?)", users_rows)

    # ---------------------------------------------------------------
    # 6. INVOICES + PAYMENTS
    #    One invoice per calendar month per active/historical lease.
    #    Issue date = 1st of month; due date = 28th of month.
    #    Payment behaviour:
    #      - Due > 6 months ago   : 91% paid
    #      - Due within 6 months  : 82% paid
    #      - Due in future        : always unpaid
    # ---------------------------------------------------------------
    print("Generating invoices and payments …")
    invoice_rows: list[tuple] = []
    payment_rows: list[tuple] = []
    inv_id  = 0
    pay_id  = 0
    SIX_MONTHS_AGO = _add_months(TODAY, -6)

    lease_data = [
        {
            "tenant_id": row[1],
            "start":     date.fromisoformat(row[3]),
            "end":       date.fromisoformat(row[4]),
            "rent":      row[5],
            "active":    row[6],
        }
        for row in leases_rows
    ]

    for lease in lease_data:
        t_id  = lease["tenant_id"]
        rent  = lease["rent"]
        l_end = min(lease["end"], TODAY)   # don't invoice beyond today

        for month_start in _month_range(lease["start"], l_end):
            inv_id   += 1
            issue_dt  = month_start
            due_dt    = date(month_start.year, month_start.month, 28)

            if due_dt > TODAY:
                paid = 0
            elif due_dt < SIX_MONTHS_AGO:
                paid = 1 if random.random() < 0.91 else 0
            else:
                paid = 1 if random.random() < 0.82 else 0

            invoice_rows.append((
                inv_id,
                t_id,
                float(rent),
                due_dt.isoformat(),
                issue_dt.isoformat(),
                paid,
            ))

            if paid:
                pay_id  += 1
                # Payment mostly arrives 1–10 days before due; occasionally 1–3 days late
                offset   = random.choices(
                    list(range(-12, 4)),
                    weights=[1, 1, 2, 3, 4, 6, 8, 10, 10, 8, 8, 7, 6, 5, 3, 2],
                )[0]
                pay_date = min(due_dt + timedelta(days=offset), TODAY)
                payment_rows.append((
                    pay_id,
                    inv_id,
                    pay_date.isoformat(),
                    float(rent),
                ))

    CHUNK = 5000

    def _bulk_insert(sql: str, data: list) -> None:
        for i in range(0, len(data), CHUNK):
            cur.executemany(sql, data[i: i + CHUNK])

    print(f"  -> {len(invoice_rows):,} invoices …")
    _bulk_insert("INSERT INTO invoices VALUES (?,?,?,?,?,?)", invoice_rows)

    print(f"  -> {len(payment_rows):,} payments …")
    _bulk_insert("INSERT INTO payments VALUES (?,?,?,?)", payment_rows)

    # ---------------------------------------------------------------
    # 7. MAINTENANCE REQUESTS
    #    ~3–5 requests per apartment per occupied year.
    # ---------------------------------------------------------------
    print("Generating maintenance requests …")
    maint_rows: list[tuple] = []
    maint_id  = 0

    # Map: apt_id -> list of (tenant_id, lease_start, lease_end_clamped)
    apt_periods: dict[int, list] = {}
    for lease in lease_data:
        apt_id_k = None
        # Lookup apartment_ID from leases_rows by lease position
        # Faster: rebuild from leases_rows directly
    for row in leases_rows:
        lid, tid, aid, lstart, lend, rent_val, active = row
        period_end = min(date.fromisoformat(lend), TODAY)
        apt_periods.setdefault(aid, []).append(
            (tid, date.fromisoformat(lstart), period_end)
        )

    for aid, periods in apt_periods.items():
        if not periods:
            continue
        window_start = min(p[1] for p in periods)
        window_end   = max(p[2] for p in periods)
        total_months = max(
            1,
            (window_end.year - window_start.year) * 12
            + window_end.month - window_start.month,
        )
        num_requests = max(1, int(total_months / 12 * random.uniform(3.0, 5.0)))

        for _ in range(num_requests):
            span_days   = max(1, (window_end - window_start).days)
            rand_day    = random.randint(0, span_days - 1)
            report_date = window_start + timedelta(days=rand_day)
            if report_date > TODAY:
                report_date = TODAY

            # Find tenant in residence on that day
            tenant_id = periods[0][0]
            for t_id, lstart, lend in periods:
                if lstart <= report_date <= lend:
                    tenant_id = t_id
                    break

            issue_desc, priority = random.choice(MAINTENANCE_ISSUES)

            sched_offset = random.randint(2, 14)
            sched_date   = report_date + timedelta(days=sched_offset)
            if sched_date > TODAY:
                sched_date = TODAY

            completed = (
                1 if sched_date < TODAY and random.random() < 0.88 else 0
            )

            base_cost = {1: 80, 2: 160, 3: 350, 4: 650, 5: 1200}[priority]
            cost = round(base_cost * random.uniform(0.7, 1.5) / 5) * 5

            maint_id += 1
            maint_rows.append((
                maint_id,
                aid,
                tenant_id,
                issue_desc,
                priority,
                report_date.isoformat(),
                sched_date.isoformat(),
                completed,
                float(cost),
            ))

    print(f"  -> {len(maint_rows):,} maintenance requests …")
    _bulk_insert(
        "INSERT INTO maintenance_requests VALUES (?,?,?,?,?,?,?,?,?)", maint_rows
    )

    # ---------------------------------------------------------------
    # 8. COMPLAINTS
    #    ~0.35 per tenant-year; only from tenants with a lease.
    # ---------------------------------------------------------------
    print("Generating complaints …")
    complaint_rows: list[tuple] = []
    comp_id = 0
    ONE_MONTH_AGO = _add_months(TODAY, -1)

    tenant_lease_spans = [
        (row[1], date.fromisoformat(row[3]), min(date.fromisoformat(row[4]), TODAY))
        for row in leases_rows
    ]

    for t_id, lstart, lend in tenant_lease_spans:
        months_tenanted = max(
            0,
            (lend.year - lstart.year) * 12 + lend.month - lstart.month,
        )
        if months_tenanted < 2:
            continue

        expected = months_tenanted / 12 * 0.35
        if random.random() > expected:
            continue
        num = random.randint(1, max(1, int(expected * 2)))

        for _ in range(num):
            span = max(14, (lend - lstart).days - 14)
            rand_day   = random.randint(14, span)
            comp_date  = lstart + timedelta(days=rand_day)
            if comp_date > TODAY:
                comp_date = TODAY
            desc     = random.choice(COMPLAINT_DESCRIPTIONS)
            resolved = (
                1 if comp_date < ONE_MONTH_AGO and random.random() < 0.80 else 0
            )
            comp_id += 1
            complaint_rows.append((
                comp_id,
                t_id,
                desc,
                comp_date.isoformat(),
                resolved,
            ))

    print(f"  -> {len(complaint_rows):,} complaints …")
    _bulk_insert("INSERT INTO complaint VALUES (?,?,?,?,?)", complaint_rows)

    # ---------------------------------------------------------------
    # Commit & print summary
    # ---------------------------------------------------------------
    conn.commit()
    conn.close()

    size_kb = os.path.getsize(DB_PATH) / 1024
    print(f"\n{'=' * 62}")
    print(f"  Paragon Apartments – database created successfully")
    print(f"{'=' * 62}")
    print(f"  Path                : {DB_PATH}")
    print(f"  Size                : {size_kb:,.1f} KB  ({size_kb/1024:.2f} MB)")
    print(f"  Date range          : {START_DATE}  ->  {TODAY}")
    print(f"  Locations           : {len(LOCATIONS)}")
    print(f"  Apartments          : {len(apartments_rows)}")
    print(f"  Tenants             : {len(tenant_pool)}")
    print(f"  Lease agreements    : {len(leases_rows):,}")
    print(f"  Invoices            : {len(invoice_rows):,}")
    print(f"  Payments            : {len(payment_rows):,}")
    print(f"  Maintenance requests: {len(maint_rows):,}")
    print(f"  Complaints          : {len(complaint_rows):,}")
    print(f"{'=' * 62}")
    print()
    print("Login credentials:")
    print("  manager                  / paragon1")
    print("  finance                  / finance1")
    print("  bristol_admin            / admin1")
    print("  bristol_frontdesk        / front1")
    print("  bristol_maintenance      / maint1")
    print("  (cardiff / london / manchester follow same pattern)")
    print()


if __name__ == "__main__":
    create_database()

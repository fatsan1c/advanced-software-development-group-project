# Paragon Apartment Management System (PAMS)

## Overview
Paragon Apartment Management System (PAMS) is a Python-based desktop application designed to improve operational efficiency for a multi-location apartment management company. It consolidates tenant, apartment, payment, and maintenance data into a secure, scalable system with role-based access control and reporting capabilities.

## Features
- User and role management (Admin, Finance, Maintenance, Manager, Front Desk)
- Tenant registration, lease tracking, and early exit handling
- Apartment management with location and occupancy details
- Payment and billing simulation with late payment notifications
- Maintenance request tracking and resolution logging
- Dynamic reporting for occupancy, financials, and maintenance costs
- Integrated database with mock data for testing and demonstration

## Tech Stack
- **Language:** Python 3.x  
- **Database:** SQLite
- **Desktop:** CustomTkinter
- **Backend API:** Flask, Flask-SQLAlchemy (optional)

## Project Structure
- **`paragonapartments/`** — Desktop app (main entry: `main.py`)
- **`backend/`** — Flask API (tenant endpoints)
- **`tests/`** — Unit and integration tests
- **`setupfiles/`** — Setup scripts and DB tools

### Recent changes
- **Backend**: Flask API with tenant endpoints; structure: `controllers/`, `services/`, `middlewares/`
- **Testing**: Pytest suite with unit + integration tests; CI on Windows, Ubuntu, macOS
- **DB**: Single `create_sqlite_testdata.py` for schema + data; `seed_testdata.py` for bulk finance data

## Installation

### Quick Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/fatsan1c/advanced-software-development-group-project.git
   cd advanced-software-development-group-project
   ```

2. Set up the virtual environment 
   > **Windows:**
   > ```powershell
   > cd setupfiles
   > powershell -ExecutionPolicy Bypass -File .\setup.ps1
   > ```
   
   > **Linux/Mac:**
   > ```bash
   > cd setupfiles
   > chmod +x setup.sh
   > ./setup.sh
   > ```
   
   - The setup script will automatically:
      - Create a virtual environment
      - Install all dependencies

3. Run the app (desktop + backend API):
   ```bash
   python paragonapartments/main.py
   ```
   Starts the desktop app and the backend API at `http://127.0.0.1:5000` (GET/POST `/tenants/`, GET `/health`).

## Database

The database includes pre-populated sample data:
- 4 locations (Bristol, Cardiff, London, Manchester)
- 40 apartments across all locations
- 40 tenants with 34 active leases
- 15 user accounts with various roles

To recreate or reset the database, run:
```bash
python setupfiles/tools/create_sqlite_testdata.py
```

## Testing (Automated + ASD Manual Test Cases)

This project includes:
- **Automated tests** (unit + SQLite integration) using `pytest`
- **Code coverage reporting** using `pytest-cov`
- **Manual test cases** (ASD deliverable) in [`docs/manual_test_cases.md`](docs/manual_test_cases.md)
- **CI pipeline** that runs tests on Ubuntu via GitHub Actions in [`.github/workflows/tests.yml`](.github/workflows/tests.yml)

### Why this is important
- **Prevents regressions**: repository/database logic is easy to break; integration tests catch issues early.
- **Safe DB testing**: tests run against a temporary SQLite database, so they do **not** modify your real app DB.
- **Assessment evidence**: manual test cases + traceability help demonstrate coverage of requirements for ASD.
- **CI confidence**: every push/PR runs the same test command to keep the project stable.

### Install dependencies
```powershell
python -m pip install -r setupfiles/requirements.txt
```

### Run automated tests
From the repository root:

```powershell
python -m pytest
```

Run a specific file:

```powershell
python -m pytest tests/test_integration.py
```

### Run coverage (and generate `coverage.xml`)
This runs the full test suite, prints a coverage table in the terminal, and writes `coverage.xml` in the repo root:

```powershell
python -m pytest --cov=paragonapartments --cov-report=term --cov-report=xml
```

- **`coverage.xml`** is a machine-readable report used by CI/tools; it can be deleted safely (it will be regenerated).

### CI outputs (GitHub Actions artifacts)
The CI workflow uploads these files for each OS run:
- **`coverage.xml`**: code coverage report (XML)
- **`pytest-results.xml`**: JUnit-style test results report (XML)

### How DB isolation works (`PAMS_DB_PATH`)
Repository code connects to SQLite through `getConnection()` in [`paragonapartments/database_operations/dbfunc.py`](paragonapartments/database_operations/dbfunc.py).

For testing (and advanced debugging), the DB path can be overridden with an environment variable:
- **`PAMS_DB_PATH`**: if set, repositories connect to that SQLite file instead of the default `paragonapartments/database/paragonapartments.db`.

Example (PowerShell):

```powershell
$env:PAMS_DB_PATH = "$PWD\temp-test.db"
python -m pytest
```

### What is covered by automated tests
- **Validation utilities**: [`paragonapartments/pages/components/input_validation.py`](paragonapartments/pages/components/input_validation.py)
- **Repository layer (SQLite integration tests)**:
  - Users: `paragonapartments/database_operations/repos/user_repository.py`
  - Locations: `paragonapartments/database_operations/repos/location_repository.py`
  - Apartments: `paragonapartments/database_operations/repos/apartment_repository.py`
  - Tenants: `paragonapartments/database_operations/repos/tenants_repository.py`
  - Finance: `paragonapartments/database_operations/repos/finance_repository.py` (including duplicate-payment prevention)

### Manual test cases (ASD)
See [`docs/manual_test_cases.md`](docs/manual_test_cases.md) for:
- Role-based scenarios (Manager / Finance / Front Desk / Maintenance)
- Preconditions, steps, expected results, and evidence guidance
- Traceability table mapping tests to features in this README

### Finance (Invoices & Payments)

The Finance area was expanded to support realistic testing and faster UI performance:

- **Finance Manager dashboard**
  - **Financial Summary** by location (auto-refresh on dropdown change) + **View Graphs** popup (Matplotlib + NumPy)
  - **Manage Invoices**: create invoice + view/edit invoices (location filter, £ formatting, pagination)
  - **Late / Unpaid Invoices**: view overdue unpaid invoices (location filter, £ formatting, pagination)
  - **Record Payment**: records a payment and marks the linked invoice as paid
  - **View Payments**: table view of payments (location filter, £ formatting, pagination)

- **Data-table improvements**
  - **Pagination (10 rows/page)** to avoid rendering all rows at once
  - Top refresh buttons next to filters for quicker workflow
  - £ currency formatting in finance tables

- **Safety: duplicate-payment prevention**
  - `record_payment` blocks payments when the invoice is already paid or already has a payment recorded, and returns a clear message.

### Performance: SQLite Indexes

For larger datasets, SQLite indexes were added to speed up the common finance queries (late/unpaid filtering, joins, and invoice/payment lookups):

- `invoices(tenant_ID)`
- `invoices(paid, due_date)`
- `payments(invoice_ID)`
- `lease_agreements(tenant_ID, active)`

Indexes are created automatically when you run `create_sqlite_testdata.py`.

### Finance Test Data Seeding (for UI / performance testing)

You can generate repeatable invoice/payment datasets across all locations using:

```bash
python setupfiles/tools/seed_testdata.py --reset --invoices 150 --paid 100 --late-unpaid 30
```
This will create:
- **150 invoices** total (default)
- **100 payments** (paid invoices)
- A guaranteed set of **late/unpaid** invoices distributed across locations (so filters like Cardiff are never empty)

After seeding, you can validate performance in the app by opening:
- Finance Manager → **View / Edit Invoices**
- Finance Manager → **Late / Unpaid Invoices**
- Finance Manager → **View Payments**

## Default Login Credentials

Change these in production environments.

| Username | Password | Role | Location |
|----------|----------|------|----------|
| manager | paragon1 | Manager | All |
| bristol_admin | admin1 | Admin | Bristol |
| finance | finance1 | Finance | All |
| bristol_frontdesk | front1 | Frontdesk | Bristol |
| bristol_maintenance | maint1 | Maintenance | Bristol |

### Permission Matrix:

| Role | Users | Apartments | Tenants | Leases | Invoices | Payments | Maintenance |
|------|-------|------------|---------|--------|----------|----------|-------------|
| **Manager** | Full | Full | Full | Full | Full | Full | Full |
| **Admin** | CRU | Full | Full | Full | CRU | CRU | Full |
| **Finance** | - | Read | Read | Read | Full | Full | - |
| **Frontdesk** | - | Read | CRU | CR | Read | Read | CR |
| **Maintenance** | - | Read | Read | - | - | - | RU |

**Legend:**
- **Full (CRUD)** = Create, Read, Update, Delete
- **CRU** = Create, Read, Update
- **CR** = Create, Read
- **RU** = Read, Update
- **Read** = Read only
- **-** = No access

## Documentation
   - Use Case, Class, and Sequence diagrams
   - Agile methodology report
   - Test case documentation and screenshots

### Assessment Context:

Developed as part of the Advanced Software Development (UFCF8S-30-2) module at UWE Bristol. This project demonstrates full software lifecycle implementation — from requirements analysis and design to coding, testing, and evaluation.
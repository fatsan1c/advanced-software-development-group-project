# Paragon Apartment Management System (PAMS)

PAMS is a desktop apartment management app built with Python, CustomTkinter, and SQLite.

## Core Features
- Role-based login for Manager, Admin, Finance, Front Desk, and Maintenance users
- Apartment, tenant, lease, invoice, payment, maintenance, and complaint management
- Multi-location support (Bristol, Cardiff, London, Manchester)
- Finance summaries and graphs by location

## Requirements
- Python 3.x available on PATH

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/fatsan1c/advanced-software-development-group-project.git
   cd advanced-software-development-group-project
   ```

2. Run the setup script:

   Windows (PowerShell):
   ```powershell
   cd setupfiles
   powershell -ExecutionPolicy Bypass -File .\setup.ps1
   ```

   Linux/macOS:
   ```bash
   cd setupfiles
   chmod +x setup.sh
   ./setup.sh
   ```

The setup script creates `.venv`, installs dependencies from `setupfiles/requirements.txt`, and creates the SQLite database if it does not already exist.

## Run
From the project root:
```bash
python paragonapartments/main.py
```

## Database Utilities
Database file location:
- `paragonapartments/database/paragonapartments.db`

Available scripts:
- Full test dataset (replaces existing DB):
  ```bash
  python setupfiles/tools/create_sqlite_testdata.py
  ```
- Empty schema + minimal seed data (4 locations + manager account):
  ```bash
  python setupfiles/tools/create_empty_sqlite_db.py
  ```

## Default Login Credentials
Common accounts:

| Username | Password | Role | Location |
|----------|----------|------|----------|
| manager | paragon1 | Manager | All |
| finance | finance1 | Finance | All |
| bristol_admin | admin1 | Admin | Bristol |
| bristol_frontdesk | front1 | Front Desk | Bristol |
| bristol_maintenance | maint1 | Maintenance | Bristol |

Other seeded city accounts follow the same pattern:
- `cardiff_admin`, `london_admin`, `manchester_admin` use `admin1`
- `cardiff_frontdesk`, `london_frontdesk`, `manchester_frontdesk` use `front1`
- `cardiff_maintenance`, `london_maintenance`, `manchester_maintenance` use `maint1`

## Tech Stack
- Python
- CustomTkinter
- SQLite
- Pillow
- passlib
- matplotlib, numpy, scipy
- tkcalendar
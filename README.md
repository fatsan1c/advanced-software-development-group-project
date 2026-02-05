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
- **GUI Framework:** CustomTkinter
- **Version Control:** Git and GitHub  

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

3. Run the Application:
   ```bash
   python paragonapartments/main.py
   ```

## Database

The database includes pre-populated sample data:
- 4 locations (Bristol, Cardiff, London, Manchester)
- 32 apartments across all locations
- 20 tenants with active leases
- 15 user accounts with various roles

To recreate or reset the database, run:
```bash
python setupfiles/tools/create_sqlite_db.py
```

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

Indexes are created automatically when you run the DB creation scripts, and can be applied to an existing DB using:

```bash
python setupfiles/tools/create_sqlite_indexes.py
```

### Finance Test Data Seeding (for UI / performance testing)

You can generate repeatable invoice/payment datasets across all locations using:

```bash
python setupfiles/tools/seed_finance_testdata.py --reset --invoices 500 --paid 300 --late-unpaid 120
```
This will create:
- **500 invoices** total
- **300 payments** (paid invoices)
- A guaranteed set of **late/unpaid** invoices distributed across locations (so filters like Cardiff are never empty)

After seeding, you can validate performance in the app by opening:
- Finance Manager → **View / Edit Invoices**
- Finance Manager → **Late / Unpaid Invoices**
- Finance Manager → **View Payments**

## Default Login Credentials

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
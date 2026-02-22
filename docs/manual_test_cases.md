# Manual Test Cases (ASD Deliverable) — Paragon Apartment Management System (PAMS)

## Test environment
- **App type**: Python desktop application (CustomTkinter)
- **Database**: SQLite (`paragonapartments/database/paragonapartments.db`)
- **Recommended OS**: Windows 10/11
- **Python**: 3.x

## Test data setup
### Reset / recreate database
Run from the repository root:

```bash
python setupfiles/tools/create_sqlite_testdata.py
```

### (Optional) Seed finance-heavy data for UI/performance testing
This creates large repeatable invoice/payment datasets across all locations:

```bash
python setupfiles/tools/seed_testdata.py --reset --invoices 150 --paid 100 --late-unpaid 30
```

## Default credentials (from `README.md`)
- `manager / paragon1` — Manager (All)
- `bristol_admin / admin1` — Admin (Bristol)
- `finance / finance1` — Finance (All)
- `bristol_frontdesk / front1` — Front Desk (Bristol)
- `bristol_maintenance / maint1` — Maintenance (Bristol)

## Traceability (features → manual test coverage)
| Feature (README) | Role(s) | Manual Test Case IDs |
|---|---|---|
| Authentication / login | All | AUTH-001…AUTH-003 |
| User & role management | Manager/Admin | USR-001…USR-004 |
| Location management | Manager | LOC-001…LOC-003 |
| Apartment management / occupancy | Manager/Admin | APT-001…APT-004 |
| Tenant registration | Front Desk | TEN-001…TEN-004 |
| Finance: invoices | Finance Manager | FIN-INV-001…FIN-INV-006 |
| Finance: payments + receipts | Finance Manager | FIN-PAY-001…FIN-PAY-005 |
| Finance: late/unpaid invoices | Finance Manager | FIN-LATE-001…FIN-LATE-003 |
| Maintenance requests tracking | Front Desk/Maintenance | MAIN-001…MAIN-003 (note: currently partial/stub UI actions) |

## Evidence capture
For each manual test case:
- Capture **screenshots** of the start state, key steps, and final result.
- Store them under `docs/evidence/<test_id>/...` (recommended) and reference the filenames in the “Evidence” field.

## Manual test cases
Each test uses the following format:
- **ID**
- **Title**
- **Role**
- **Preconditions**
- **Steps**
- **Expected**
- **Evidence**

---

### Authentication
#### AUTH-001 — Valid login (role routing)
- **Role**: Any
- **Preconditions**: DB exists; user credentials are present.
- **Steps**:
  1. Run `python paragonapartments/main.py`.
  2. Enter valid username/password (e.g. `finance / finance1`).
  3. Click **Login**.
- **Expected**:
  - Login succeeds.
  - Home dashboard shows the correct **role** and **location** at the top.
- **Evidence**: Screenshot of successful landing page.

#### AUTH-002 — Invalid login rejected
- **Role**: Any
- **Preconditions**: App running.
- **Steps**:
  1. Enter an existing username with a wrong password (or any invalid pair).
  2. Click **Login**.
- **Expected**:
  - Error message “Invalid credentials…” is displayed.
  - User is not routed to the Home page.
- **Evidence**: Screenshot of error message.

#### AUTH-003 — Logout returns to login
- **Role**: Any
- **Preconditions**: Logged in.
- **Steps**:
  1. Click **Logout**.
- **Expected**:
  - Home page closes.
  - Login window reappears.
- **Evidence**: Screenshot of login page after logout.

---

### User & role management (Manager/Admin)
#### USR-001 — Manager creates a user account
- **Role**: Manager
- **Preconditions**: Logged in as `manager`.
- **Steps**:
  1. Open **Manage Staff User Accounts**.
  2. Fill out username, role, password, and (optional) location.
  3. Submit.
- **Expected**:
  - Success confirmation shown.
  - New account appears in the users table/list (if available).
- **Evidence**: Screenshots of form and confirmation/list.

#### USR-002 — Manager edits a user account
- **Role**: Manager
- **Preconditions**: At least one user exists.
- **Steps**:
  1. Open users table/list.
  2. Select a user.
  3. Change role and/or location.
  4. Save/update.
- **Expected**:
  - Changes persist and are visible on refresh.
- **Evidence**: Before/after screenshots.

#### USR-003 — Manager deletes a user account
- **Role**: Manager
- **Preconditions**: A non-critical user exists (do not delete your active login).
- **Steps**:
  1. Open users table/list.
  2. Delete the target user.
- **Expected**:
  - User no longer appears in list.
  - Login with deleted account fails (AUTH-002).
- **Evidence**: Screenshot after deletion + failed login.

#### USR-004 — Change password (self-service)
- **Role**: Any
- **Preconditions**: Logged in.
- **Steps**:
  1. Click **Change password**.
  2. Enter old password + new password.
  3. Submit.
  4. Logout and log back in with new password.
- **Expected**:
  - Password change succeeds.
  - Old password no longer works; new password works.
- **Evidence**: Screenshot of success + successful re-login.

---

### Location management (Manager)
#### LOC-001 — Add location
- **Role**: Manager
- **Preconditions**: Logged in as `manager`.
- **Steps**:
  1. Open business expansion / location management.
  2. Enter new city + address.
  3. Submit.
- **Expected**:
  - Location is added and appears in dropdowns (e.g., Finance/Occupancy filters).
- **Evidence**: Screenshot of new city appearing in dropdown.

#### LOC-002 — Edit location
- **Role**: Manager
- **Preconditions**: A location exists.
- **Steps**:
  1. Edit an existing location’s city/address.
  2. Save.
- **Expected**:
  - Updates persist; dropdowns reflect the new city name.
- **Evidence**: Before/after screenshots.

#### LOC-003 — Delete location (safe handling)
- **Role**: Manager
- **Preconditions**: A location exists with **no dependent apartments/users** (or validate expected constraint error).
- **Steps**:
  1. Delete the location.
- **Expected**:
  - If dependencies exist: operation fails with a clear error (foreign key constraint), and the app remains stable.
  - If no dependencies exist: location removed and no longer selectable.
- **Evidence**: Screenshot of outcome.

---

### Apartments / occupancy (Manager/Admin)
#### APT-001 — View occupancy summary (All vs single location)
- **Role**: Manager
- **Preconditions**: Logged in as `manager`.
- **Steps**:
  1. Open **Apartment Occupancy**.
  2. Select **All Locations** and note values.
  3. Select a single city and note values.
- **Expected**:
  - Counts update correctly when dropdown changes.
- **Evidence**: Screenshots for both dropdown selections.

#### APT-002 — Add apartment
- **Role**: Manager
- **Preconditions**: A location exists.
- **Steps**:
  1. Add an apartment with rent, beds, status.
  2. Refresh apartment list/table.
- **Expected**:
  - New apartment appears with correct status.
- **Evidence**: Screenshot of list including new apartment.

#### APT-003 — Edit apartment
- **Role**: Manager
- **Preconditions**: At least one apartment exists.
- **Steps**:
  1. Edit rent/beds/status for an apartment.
  2. Save.
- **Expected**:
  - Changes persist and are visible after refresh.
- **Evidence**: Before/after screenshots.

#### APT-004 — Delete apartment
- **Role**: Manager
- **Preconditions**: A deletable apartment exists.
- **Steps**:
  1. Delete an apartment.
- **Expected**:
  - Apartment no longer appears in list.
- **Evidence**: Screenshot after deletion.

---

### Tenant registration (Front Desk)
#### TEN-001 — Register tenant (happy path)
- **Role**: Front Desk
- **Preconditions**: Logged in as `bristol_frontdesk`.
- **Steps**:
  1. Open **Register Tenant** form.
  2. Fill all required fields with valid values.
  3. Submit.
- **Expected**:
  - Success confirmation; tenant is stored.
- **Evidence**: Screenshot of confirmation.

#### TEN-002 — Register tenant (invalid email)
- **Role**: Front Desk
- **Preconditions**: Form open.
- **Steps**:
  1. Enter an invalid email (e.g. `not-an-email`).
  2. Submit.
- **Expected**:
  - Form rejects submission or shows an error (depending on UI validation implementation).
- **Evidence**: Screenshot of validation/error.

#### TEN-003 — Register tenant (invalid phone)
- **Role**: Front Desk
- **Steps**:
  1. Enter invalid phone (e.g. `06123456789`).
  2. Submit.
- **Expected**:
  - Validation error.
- **Evidence**: Screenshot.

#### TEN-004 — Register tenant (duplicate NI/email)
- **Role**: Front Desk
- **Preconditions**: A tenant exists with the NI/email.
- **Steps**:
  1. Register another tenant using the same NI number or email.
- **Expected**:
  - Operation fails (SQLite UNIQUE constraint) and app remains stable with a clear error.
- **Evidence**: Screenshot of error.

---

### Finance (Finance Manager)
#### FIN-INV-001 — Create invoice (valid)
- **Role**: Finance Manager
- **Preconditions**: Logged in as `finance`; a tenant exists.
- **Steps**:
  1. Open **Create Invoice**.
  2. Enter Tenant ID, Amount Due > 0, Due Date.
  3. Submit.
- **Expected**:
  - Invoice created successfully.
- **Evidence**: Screenshot of confirmation or invoice appearing in list.

#### FIN-INV-002 — Create invoice (invalid: amount <= 0)
- **Role**: Finance Manager
- **Steps**:
  1. Enter Amount Due `0` or negative.
  2. Submit.
- **Expected**:
  - Validation blocks creation with an error message.
- **Evidence**: Screenshot.

#### FIN-INV-003 — View/Edit invoices filtered by location
- **Role**: Finance Manager
- **Preconditions**: Invoices exist across multiple cities (use seeding tool if needed).
- **Steps**:
  1. Open **View / Edit Invoices**.
  2. Select a city filter.
  3. Refresh.
- **Expected**:
  - Only invoices from that city appear.
- **Evidence**: Screenshot of filtered list.

#### FIN-INV-004 — Update invoice row
- **Role**: Finance Manager
- **Steps**:
  1. Edit amount/due date/paid flag for an invoice row.
  2. Save/update.
- **Expected**:
  - Update persists and is visible after refresh.
- **Evidence**: Before/after screenshots.

#### FIN-INV-005 — Delete invoice row
- **Role**: Finance Manager
- **Steps**:
  1. Delete an invoice.
- **Expected**:
  - Invoice removed from the list after refresh.
- **Evidence**: Screenshot after deletion.

#### FIN-LATE-001 — Late/unpaid invoices list populated
- **Role**: Finance Manager
- **Preconditions**: Late/unpaid invoices exist (use seeding tool).
- **Steps**:
  1. Open **Late / Unpaid Invoices**.
- **Expected**:
  - List shows unpaid invoices with due dates in the past.
- **Evidence**: Screenshot of late list.

#### FIN-LATE-002 — Late/unpaid filter by location
- **Role**: Finance Manager
- **Steps**:
  1. Select a city in the late/unpaid view.
- **Expected**:
  - Results change to only that city.
- **Evidence**: Screenshot.

#### FIN-PAY-001 — Record payment (valid)
- **Role**: Finance Manager
- **Preconditions**: An unpaid invoice exists.
- **Steps**:
  1. Open **Record Payment**.
  2. Enter matching Invoice ID + Tenant ID + Amount.
  3. Submit.
- **Expected**:
  - Payment row is created.
  - Invoice is marked paid.
- **Evidence**: Screenshot of success + invoice paid state.

#### FIN-PAY-002 — Record payment blocked when invoice already paid
- **Role**: Finance Manager
- **Preconditions**: A paid invoice exists.
- **Steps**:
  1. Attempt to record payment for a paid invoice.
- **Expected**:
  - Operation blocked with clear message (“already marked as paid”).
- **Evidence**: Screenshot.

#### FIN-PAY-003 — Record payment blocked when payment already exists
- **Role**: Finance Manager
- **Preconditions**: A payment already exists for the invoice.
- **Steps**:
  1. Attempt to record a second payment for the same invoice.
- **Expected**:
  - Operation blocked with clear message (“already recorded”).
- **Evidence**: Screenshot.

#### FIN-PAY-004 — View payments table filtered by location
- **Role**: Finance Manager
- **Steps**:
  1. Open **View Payments**.
  2. Filter by city.
- **Expected**:
  - Only payments for that city appear.
- **Evidence**: Screenshot.

---

### Maintenance (Front Desk / Maintenance)
> Note: As of current implementation, several maintenance actions appear to be placeholders (e.g., printing messages). Treat these as **partial** acceptance tests unless expanded.

#### MAIN-001 — Front Desk opens maintenance request UI
- **Role**: Front Desk
- **Steps**:
  1. Open the **Maintenance Requests** area.
- **Expected**:
  - UI opens without crashing.
- **Evidence**: Screenshot.

#### MAIN-002 — Maintenance staff “view requests” action
- **Role**: Maintenance
- **Steps**:
  1. Click **View Requests**.
- **Expected**:
  - App remains stable; expected action occurs (currently may only log output).
- **Evidence**: Screenshot + captured console output (if required).

#### MAIN-003 — Maintenance staff “update status” action
- **Role**: Maintenance
- **Steps**:
  1. Click **Update Request**.
- **Expected**:
  - App remains stable; expected action occurs (currently may only log output).
- **Evidence**: Screenshot + captured console output.


"""Integration tests: repository CRUD and business logic."""

import pytest


def test_occupancy_and_revenue(seed_minimal_data):
    import database_operations.repos.apartment_repository as apartment_repo

    # Seed data has two occupied apartments (one per location)
    assert apartment_repo.get_all_occupancy() == 2
    assert apartment_repo.get_total_apartments() == 2

    assert apartment_repo.get_all_occupancy("Bristol") == 1
    assert apartment_repo.get_total_apartments("Bristol") == 1

    assert apartment_repo.get_monthly_revenue("Bristol") == 900.0
    assert apartment_repo.get_potential_revenue("Bristol") == 900.0


def test_apartment_crud(seed_minimal_data):
    import database_operations.repos.apartment_repository as apartment_repo
    import database_operations.repos.location_repository as location_repo

    bristol_id = location_repo.get_location_id_by_city("Bristol")

    ok = apartment_repo.create_apartment(bristol_id, "New Flat", 3, 1500.0, 0)
    assert ok is True

    apartments = apartment_repo.get_all_apartments()
    new_row = next(a for a in apartments if a["apartment_address"] == "New Flat")
    apt_id = int(new_row["apartment_ID"])

    assert apartment_repo.update_apartment(apt_id, occupied=1) is True
    assert apartment_repo.delete_apartment(apt_id) is True


def test_get_invoices_and_location_enrichment(seed_minimal_data):
    import database_operations.repos.finance_repository as finance_repo

    invoices = finance_repo.get_invoices()
    assert len(invoices) >= 2

    # Should include enriched fields
    row = invoices[0]
    assert "tenant_name" in row
    assert "city" in row

    bristol_invoices = finance_repo.get_invoices("Bristol")
    assert all(r["city"] == "Bristol" for r in bristol_invoices)


def test_late_invoices_as_of(seed_minimal_data):
    import database_operations.repos.finance_repository as finance_repo

    # Seed unpaid invoice due 2025-12-01 should be late as of 2026-01-01
    late = finance_repo.get_late_invoices(as_of="2026-01-01")
    assert any(
        int(r["invoice_ID"]) == seed_minimal_data["invoices"]["unpaid"] for r in late
    )

    not_late_yet = finance_repo.get_late_invoices(as_of="2025-11-15")
    assert all(
        int(r["invoice_ID"]) != seed_minimal_data["invoices"]["unpaid"]
        for r in not_late_yet
    )


def test_record_payment_happy_path_and_guards(seed_minimal_data):
    import database_operations.repos.finance_repository as finance_repo

    alice_id = seed_minimal_data["tenants"]["alice"]

    # Happy path: record payment and mark invoice as paid
    invoice_mark_paid = finance_repo.create_invoice(
        alice_id, 100.0, "2026-01-10", issue_date="2026-01-01", paid=0
    )
    payment_id = finance_repo.record_payment(
        invoice_mark_paid,
        alice_id,
        100.0,
        payment_date="2026-01-02",
        mark_invoice_paid=True,
    )
    assert isinstance(payment_id, int)

    inv = finance_repo.get_invoice_by_id(invoice_mark_paid)
    assert int(inv["paid"]) == 1

    # Attempting to pay again fails (invoice is already paid)
    with pytest.raises(ValueError, match="already marked as paid"):
        finance_repo.record_payment(
            invoice_mark_paid, alice_id, 100.0, payment_date="2026-01-03"
        )

    # Duplicate payment prevented (even if invoice isn't marked paid)
    invoice_keep_unpaid = finance_repo.create_invoice(
        alice_id, 50.0, "2026-02-01", issue_date="2026-01-01", paid=0
    )
    payment_id2 = finance_repo.record_payment(
        invoice_keep_unpaid,
        alice_id,
        50.0,
        payment_date="2026-01-05",
        mark_invoice_paid=False,
    )
    assert isinstance(payment_id2, int)
    inv2 = finance_repo.get_invoice_by_id(invoice_keep_unpaid)
    assert int(inv2["paid"]) == 0

    with pytest.raises(ValueError, match="already been recorded"):
        finance_repo.record_payment(
            invoice_keep_unpaid,
            alice_id,
            50.0,
            payment_date="2026-01-06",
            mark_invoice_paid=False,
        )

    # Paying an already-paid invoice prevented (seed has one paid invoice)
    paid_invoice_id = seed_minimal_data["invoices"]["paid"]
    bob_id = seed_minimal_data["tenants"]["bob"]
    with pytest.raises(ValueError, match="already marked as paid"):
        finance_repo.record_payment(paid_invoice_id, bob_id, 200.0)

    # Wrong tenant prevented
    another_unpaid = finance_repo.create_invoice(
        alice_id, 60.0, "2026-02-02", issue_date="2026-01-01", paid=0
    )
    with pytest.raises(ValueError, match="belongs to tenant ID"):
        finance_repo.record_payment(another_unpaid, bob_id, 50.0)


def test_financial_summary(seed_minimal_data):
    import database_operations.repos.finance_repository as finance_repo

    summary_all = finance_repo.get_financial_summary(as_of="2026-01-01")
    assert summary_all["total_invoiced"] >= 300.0
    assert summary_all["total_collected"] >= 200.0
    assert summary_all["outstanding"] == pytest.approx(
        summary_all["total_invoiced"] - summary_all["total_collected"]
    )
    assert summary_all["late_invoice_count"] >= 1

    summary_bristol = finance_repo.get_financial_summary("Bristol", as_of="2026-01-01")
    assert summary_bristol["late_invoice_count"] >= 1


def test_location_crud(seed_minimal_data):
    import database_operations.repos.location_repository as location_repo

    cities = location_repo.get_all_cities()
    assert "Bristol" in cities
    assert "Cardiff" in cities

    location_id = location_repo.create_location("Testville", "99 Example Rd")
    assert isinstance(location_id, int)

    loc = location_repo.get_location_by_id(location_id)
    assert loc["city"] == "Testville"

    assert location_repo.update_location(location_id, city="Testopolis") is True
    assert (
        location_repo.get_location_by_city("Testopolis")["location_ID"] == location_id
    )

    stats = location_repo.get_location_stats(location_id)
    assert stats["apartment_count"] == 0

    assert location_repo.delete_location(location_id) is True
    assert location_repo.get_location_by_id(location_id) is None


def test_create_tenant_persists(seed_minimal_data):
    import database_operations.repos.tenants_repository as tenants_repo
    from database_operations.db_execute import execute_query

    tenant_id = tenants_repo.create_tenant(
        first_name="Charlie",
        last_name="Tenant",
        date_of_birth="1992-02-02",
        NI_number="AE123456C",
        email="charlie@example.com",
        phone="07111222333",
        occupation="Nurse",
        annual_salary=38000,
        right_to_rent="Y",
        credit_check="Passed",
        pets="N",
    )
    assert isinstance(tenant_id, int)

    row = execute_query(
        "SELECT tenant_ID, first_name, last_name, email FROM tenants WHERE tenant_ID = ?",
        (tenant_id,),
        fetch_one=True,
    )
    assert row is not None
    assert row["email"] == "charlie@example.com"


def test_create_and_authenticate_user(seed_minimal_data):
    import database_operations.repos.user_repository as user_repo

    bristol_id = seed_minimal_data["locations"]["bristol"]

    user_id = user_repo.create_user("testuser", "secret123", "Manager", bristol_id)
    assert isinstance(user_id, int)

    auth = user_repo.authenticate_user("testuser", "secret123")
    assert auth is not None
    assert auth["username"] == "testuser"
    assert auth["role"] == "Manager"
    assert auth["city"] == "Bristol"

    assert user_repo.validate_credentials("testuser", "secret123") is True
    assert user_repo.validate_credentials("testuser", "wrong") is False


def test_update_user_and_change_password(seed_minimal_data):
    import database_operations.repos.user_repository as user_repo

    cardiff_id = seed_minimal_data["locations"]["cardiff"]
    user_id = user_repo.create_user("pwuser", "oldpw", "Admin", cardiff_id)

    # Update role + location
    assert user_repo.update_user(user_id, role="Finance", location_ID=None) is True
    updated = user_repo.get_user_by_id(user_id)
    assert updated["role"] == "Finance"
    assert updated["city"] is None

    # Change password
    assert user_repo.change_password("pwuser", "oldpw", "newpw") is True
    assert user_repo.validate_credentials("pwuser", "oldpw") is False
    assert user_repo.validate_credentials("pwuser", "newpw") is True


def test_delete_user(seed_minimal_data):
    import database_operations.repos.user_repository as user_repo

    user_id = user_repo.create_user("deluser", "pw", "Manager", None)
    assert user_repo.get_user_by_id(user_id) is not None

    assert user_repo.delete_user(user_id) is True
    assert user_repo.get_user_by_id(user_id) is None


def test_get_maintenance_requests_empty(seed_minimal_data):
    import database_operations.repos.maintenance_repository as maintenance_repo

    # Seed has no maintenance requests
    requests = maintenance_repo.get_maintenance_requests()
    assert requests == [] or len(requests) == 0


def test_create_and_update_maintenance_request(seed_minimal_data):
    import database_operations.repos.maintenance_repository as maintenance_repo

    apt_id = seed_minimal_data["apartments"]["apt1"]
    tenant_id = seed_minimal_data["tenants"]["alice"]

    request_id = maintenance_repo.create_maintenance_request(
        apartment_id=apt_id,
        tenant_id=tenant_id,
        issue_description="Leaking faucet",
        priority_level=3,
        reported_date="2025-11-15",
    )
    assert isinstance(request_id, int)

    requests = maintenance_repo.get_maintenance_requests()
    assert len(requests) >= 1
    found = next(r for r in requests if int(r["request_ID"]) == request_id)
    assert found["issue_description"] == "Leaking faucet"
    assert int(found["completed"]) == 0

    assert maintenance_repo.mark_maintenance_completed(request_id, cost=85.50) is True
    updated = maintenance_repo.get_maintenance_request_by_id(request_id)
    assert int(updated["completed"]) == 1
    assert float(updated["cost"]) == 85.50

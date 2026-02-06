import pytest


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
    assert any(int(r["invoice_ID"]) == seed_minimal_data["invoices"]["unpaid"] for r in late)

    not_late_yet = finance_repo.get_late_invoices(as_of="2025-11-15")
    assert all(int(r["invoice_ID"]) != seed_minimal_data["invoices"]["unpaid"] for r in not_late_yet)


def test_record_payment_happy_path_and_guards(seed_minimal_data):
    import database_operations.repos.finance_repository as finance_repo

    alice_id = seed_minimal_data["tenants"]["alice"]

    # Happy path: record payment and mark invoice as paid
    invoice_mark_paid = finance_repo.create_invoice(alice_id, 100.0, "2026-01-10", issue_date="2026-01-01", paid=0)
    payment_id = finance_repo.record_payment(invoice_mark_paid, alice_id, 100.0, payment_date="2026-01-02", mark_invoice_paid=True)
    assert isinstance(payment_id, int)

    inv = finance_repo.get_invoice_by_id(invoice_mark_paid)
    assert int(inv["paid"]) == 1

    # Attempting to pay again fails (invoice is already paid)
    with pytest.raises(ValueError, match="already marked as paid"):
        finance_repo.record_payment(invoice_mark_paid, alice_id, 100.0, payment_date="2026-01-03")

    # Duplicate payment prevented (even if invoice isn't marked paid)
    invoice_keep_unpaid = finance_repo.create_invoice(alice_id, 50.0, "2026-02-01", issue_date="2026-01-01", paid=0)
    payment_id2 = finance_repo.record_payment(invoice_keep_unpaid, alice_id, 50.0, payment_date="2026-01-05", mark_invoice_paid=False)
    assert isinstance(payment_id2, int)
    inv2 = finance_repo.get_invoice_by_id(invoice_keep_unpaid)
    assert int(inv2["paid"]) == 0

    with pytest.raises(ValueError, match="already been recorded"):
        finance_repo.record_payment(invoice_keep_unpaid, alice_id, 50.0, payment_date="2026-01-06", mark_invoice_paid=False)

    # Paying an already-paid invoice prevented (seed has one paid invoice)
    paid_invoice_id = seed_minimal_data["invoices"]["paid"]
    bob_id = seed_minimal_data["tenants"]["bob"]
    with pytest.raises(ValueError, match="already marked as paid"):
        finance_repo.record_payment(paid_invoice_id, bob_id, 200.0)

    # Wrong tenant prevented
    another_unpaid = finance_repo.create_invoice(alice_id, 60.0, "2026-02-02", issue_date="2026-01-01", paid=0)
    with pytest.raises(ValueError, match="belongs to tenant ID"):
        finance_repo.record_payment(another_unpaid, bob_id, 50.0)


def test_financial_summary(seed_minimal_data):
    import database_operations.repos.finance_repository as finance_repo

    summary_all = finance_repo.get_financial_summary(as_of="2026-01-01")
    assert summary_all["total_invoiced"] >= 300.0
    assert summary_all["total_collected"] >= 200.0
    assert summary_all["outstanding"] == pytest.approx(summary_all["total_invoiced"] - summary_all["total_collected"])
    assert summary_all["late_invoice_count"] >= 1

    summary_bristol = finance_repo.get_financial_summary("Bristol", as_of="2026-01-01")
    assert summary_bristol["late_invoice_count"] >= 1


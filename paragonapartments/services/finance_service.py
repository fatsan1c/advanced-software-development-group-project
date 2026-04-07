"""Finance business operations extracted from UI-facing role classes."""

from __future__ import annotations

from database_operations.database_repositories import (
    get_all_tenant_names,
    invoices_repo,
    payments_repo,
)
import pages.components.input_validation as input_validation


class FinanceService:
    """Domain/service layer for finance operations."""

    @staticmethod
    def generate_financial_reports(location: str = "all"):
        """Return financial summary data used by dashboards."""
        return invoices_repo.get_financial_summary(location)

    @staticmethod
    def get_finance_date_range(location: str, grouping: str = "month"):
        """Return available finance date range for graph filters."""
        return invoices_repo.get_finance_date_range(location, grouping=grouping)

    @staticmethod
    def get_unpaid_invoices(location: str = "all"):
        """Return unpaid invoices for the given location scope."""
        return invoices_repo.get_invoices(location=location, paid=0)

    @staticmethod
    def get_invoices(location: str = "all", paid: int | None = None):
        """Return invoices for the given location with optional paid filter."""
        return invoices_repo.get_invoices(location=location, paid=paid)

    @staticmethod
    def get_late_invoices(location: str = "all"):
        """Return late invoices for the given location scope."""
        return invoices_repo.get_late_invoices(location)

    @staticmethod
    def get_payments(location: str = "all"):
        """Return payment records for the given location scope."""
        return payments_repo.get_payments(location)

    @staticmethod
    def get_all_tenant_names():
        """Return tenant list used by invoice creation dropdowns."""
        return get_all_tenant_names()

    @staticmethod
    def normalize_date(date_str: str | None) -> str | None:
        """Normalize UI date value to database format (YYYY-MM-DD)."""
        return input_validation.normalize_date_to_db(date_str)

    @classmethod
    def create_invoice(cls, values):
        """Create a new invoice."""
        try:
            tenant_id = values.get("Tenant")
            if tenant_id:
                tenant_id = int(tenant_id)
            amount_due = float(values.get("Amount Due", 0))
            due_date = cls.normalize_date(values.get("Due Date", ""))
            issue_date = cls.normalize_date(values.get("Issue Date", "")) or None

            if not tenant_id:
                return "Tenant is required."
            if not due_date:
                return "Due Date is required (YYYY-MM-DD)."
            if amount_due <= 0:
                return "Amount Due must be greater than 0."

            invoice_id = invoices_repo.create_invoice(
                tenant_id=tenant_id,
                amount_due=amount_due,
                due_date=due_date,
                issue_date=issue_date,
                paid=0,
            )
            return True if invoice_id else "Failed to create invoice."
        except Exception as e:
            return f"Failed to create invoice: {str(e)}"

    @classmethod
    def update_invoice_row(cls, row_data, updated_data):
        """Update an invoice row from editable table data."""
        try:
            invoice_id = int(row_data.get("invoice_ID"))
            kwargs = {}

            if "tenant_ID" in updated_data:
                kwargs["tenant_ID"] = int(updated_data["tenant_ID"])
            if "amount_due" in updated_data:
                kwargs["amount_due"] = float(updated_data["amount_due"])
            if "due_date" in updated_data:
                kwargs["due_date"] = cls.normalize_date(updated_data["due_date"])
            if "issue_date" in updated_data:
                kwargs["issue_date"] = cls.normalize_date(updated_data["issue_date"])
            if "paid" in updated_data:
                kwargs["paid"] = int(updated_data["paid"])

            success = invoices_repo.update_invoice(invoice_id, **kwargs)
            return True if success else "Update failed."
        except Exception as e:
            return f"Failed to update invoice: {str(e)}"

    @staticmethod
    def delete_invoice_row(row_data):
        """Delete an invoice row from the table."""
        try:
            invoice_id = int(row_data.get("invoice_ID"))
            success = invoices_repo.delete_invoice(invoice_id)
            return True if success else "Delete failed."
        except Exception as e:
            return f"Failed to delete invoice: {str(e)}"

    @classmethod
    def record_payment(cls, values):
        """Record a payment and mark invoice as paid."""
        try:
            invoice_id = values.get("Invoice")
            if invoice_id:
                invoice_id = int(invoice_id)
            amount = float(values.get("Amount", 0))
            payment_date = cls.normalize_date(values.get("Payment Date", "")) or None

            if not invoice_id:
                return "Invoice is required."
            if amount <= 0:
                return "Amount must be greater than 0."

            invoice = invoices_repo.get_invoice_by_id(invoice_id)
            if not invoice:
                return f"Invoice ID {invoice_id} does not exist."
            if int(invoice.get("paid") or 0) == 1:
                return f"Invoice {invoice_id} is already marked as paid."

            payment_id = payments_repo.record_payment(
                invoice_id=invoice_id,
                amount=amount,
                payment_date=payment_date,
                mark_invoice_paid=True,
            )
            return True if payment_id else "Failed to record payment."
        except Exception as e:
            return f"Failed to record payment: {str(e)}"

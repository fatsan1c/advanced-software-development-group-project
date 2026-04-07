from pages.components.dashboard_cards import (
    load_finance_invoice_card,
    load_finance_payments_card,
    load_finance_summary_card,
    render_dashboard_cards,
)
from models.user import User
from services.finance_service import FinanceService


class FinanceManager(User):
    """Finance manager with financial reporting and payment processing capabilities."""

    CARD_SEQUENCE = [
        {"row": 1, "builder": load_finance_summary_card},
        {"row": 2, "builder": load_finance_payments_card},
        {"row": 3, "builder": load_finance_invoice_card},
    ]

    def __init__(self, username: str, location: str | None = None):
        super().__init__(username, role="Finance Manager", location=location)

    def load_homepage_content(self, home_page):
        """Render finance dashboard cards in configured order."""
        super().load_homepage_content(home_page)
        render_dashboard_cards(home_page, self, self.CARD_SEQUENCE)

    def generate_financial_reports(self, location: str = "all"):
        """Return finance summary metrics for the selected location."""
        return FinanceService.generate_financial_reports(location)

    def get_finance_date_range(self, location: str, grouping: str = "month"):
        """Return finance graph date range for the selected location."""
        return FinanceService.get_finance_date_range(location, grouping=grouping)

    def get_unpaid_invoices(self, location: str = "all"):
        """Return unpaid invoices for the selected location."""
        return FinanceService.get_unpaid_invoices(location)

    def get_invoices(self, location: str = "all", paid: int | None = None):
        """Return invoices for the selected location."""
        return FinanceService.get_invoices(location, paid=paid)

    def get_late_invoices(self, location: str = "all"):
        """Return late invoices for the selected location."""
        return FinanceService.get_late_invoices(location)

    def get_payments(self, location: str = "all"):
        """Return payment records for the selected location."""
        return FinanceService.get_payments(location)

    def get_all_tenant_names(self):
        """Return tenant names for invoice dropdowns."""
        return FinanceService.get_all_tenant_names()

    def create_invoice(self, values):
        """Create a new invoice."""
        return FinanceService.create_invoice(values)

    def update_invoice_row(self, row_data, updated_data):
        """Update an existing invoice row."""
        return FinanceService.update_invoice_row(row_data, updated_data)

    def delete_invoice_row(self, row_data):
        """Delete an invoice row."""
        return FinanceService.delete_invoice_row(row_data)

    def record_payment(self, values):
        """Record a payment for an invoice."""
        return FinanceService.record_payment(values)

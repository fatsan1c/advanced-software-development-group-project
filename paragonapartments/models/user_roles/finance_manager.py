import pages.components.page_elements as pe
from models.user import User


class FinanceManager(User):
    """Finance manager with financial reporting and payment processing capabilities."""
    
    def __init__(self, username: str, location: str = None):
        super().__init__(username, role="Finance Manager", location=location)

# ============================= v Admin functions v  =====================================
    def generate_financial_reports(self):
        """Generate financial reports across all locations."""
        print("Generating financial reports...")

    def manage_invoices(self):
        """Manage invoices across all locations."""
        print("Managing invoices...")

    def view_late_payments(self):
        """View all late payments across the system."""
        print("Viewing late payments...")

    def process_payments(self, payment_id: int):
        """Process a payment with the given payment ID."""
        print(f"Processing payment with ID: {payment_id}")
    
# ============================= ^ Admin functions ^ =====================================
    
# ============================= v Homepage UI Content v =====================================
    def load_homepage_content(self, home_page, home_page_instance=None):
        """Load Finance Manager-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page, home_page_instance)

        row1 = pe.row_container(parent=home_page)
        
        # Add financial management cards
        self.load_reports_content(row1)

        self.load_invoices_content(row1)

        row2 = pe.row_container(parent=home_page)

        # Add payment processing function cards
        self.load_payment_content(row2)

        self.load_process_content(row2)

    def load_reports_content(self, row):
        reports_card = pe.function_card(row, "Financial Reports", side="left")
        
        pe.action_button(
            reports_card,
            text="Generate Reports",
            command=lambda: self.generate_financial_reports()
        )

    def load_invoices_content(self, row):
        invoices_card = pe.function_card(row, "Manage Invoices", side="left")

        pe.action_button(
            invoices_card,
            text="View Invoices",
            command=lambda: self.manage_invoices()
        )

    def load_payment_content(self, row):
        payments_card = pe.function_card(row, "Late Payments", side="left")

        pe.action_button(
            payments_card,
            text="View Late Payments",
            command=lambda: self.view_late_payments()
        )

    def load_process_content(self, row):
        process_card = pe.function_card(row, "Process Payments", side="left")

        pe.action_button(
            process_card,
            text="Process Payment",
            command=lambda: self.process_payments(1)
        )
# ============================= ^ Homepage UI Content ^ =====================================
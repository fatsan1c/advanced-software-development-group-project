import customtkinter as ctk
import pages.components.page_elements as pe
import pages.components.input_validation as input_validation
from database_operations.database_repositories import (
    invoices_repo, 
    payments_repo, 
    get_all_tenant_names
)
from services import FinanceGraphService
from models.user import User


class FinanceManager(User):
    """Finance manager with financial reporting and payment processing capabilities."""
    
    def __init__(self, username: str, location: str = None):
        super().__init__(username, role="Finance Manager", location=location)

# ============================= v Finance Manager functions v  =====================================
    def generate_financial_reports(self, location: str = "all"):
        """Return financial summary data (used by the dashboard)."""
        return invoices_repo.get_financial_summary(location)
    
    def format_financial_stats(self, location: str = "all") -> str:
        """Format financial summary as stats text string for reports.
        
        Args:
            location: Location to get summary for (default: "all")
            
        Returns:
            str: Formatted stats text with invoiced, collected, outstanding, and late invoices
        """
        summary = self.generate_financial_reports(location)
        return (f"Total Invoiced: £{summary['total_invoiced']:,.2f}\n"
                f"Total Collected: £{summary['total_collected']:,.2f}\n"
                f"Outstanding: £{summary['outstanding']:,.2f}\n"
                f"Late Invoices: {summary['late_invoice_count']}")

    def _ui_date_to_db(self, date_str: str | None) -> str | None:
        """
        Validate and normalize UI date string to database format (YYYY-MM-DD).
        Returns None for blank values.
        Uses centralized input_validation module.
        """
        return input_validation.normalize_date_to_db(date_str)

    def create_invoice(self, values):
        """Create a new invoice."""
        try:
            tenant_id = values.get("Tenant")
            if tenant_id:
                tenant_id = int(tenant_id)
            amount_due = float(values.get("Amount Due", 0))
            due_date = self._ui_date_to_db(values.get("Due Date", ""))
            issue_date = self._ui_date_to_db(values.get("Issue Date", "")) or None

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
                paid=0
            )
            return True if invoice_id else "Failed to create invoice."
        except Exception as e:
            return f"Failed to create invoice: {str(e)}"

    def update_invoice_row(self, row_data, updated_data):
        """Update an invoice row from the editable table."""
        try:
            invoice_id = int(row_data.get("invoice_ID"))
            kwargs = {}

            if "tenant_ID" in updated_data:
                kwargs["tenant_ID"] = int(updated_data["tenant_ID"])
            if "amount_due" in updated_data:
                kwargs["amount_due"] = float(updated_data["amount_due"])
            if "due_date" in updated_data:
                kwargs["due_date"] = self._ui_date_to_db(updated_data["due_date"])
            if "issue_date" in updated_data:
                kwargs["issue_date"] = self._ui_date_to_db(updated_data["issue_date"])
            if "paid" in updated_data:
                kwargs["paid"] = int(updated_data["paid"])

            success = invoices_repo.update_invoice(invoice_id, **kwargs)
            return True if success else "Update failed."
        except Exception as e:
            return f"Failed to update invoice: {str(e)}"

    def delete_invoice_row(self, row_data):
        """Delete an invoice row from the table."""
        try:
            invoice_id = int(row_data.get("invoice_ID"))
            success = invoices_repo.delete_invoice(invoice_id)
            return True if success else "Delete failed."
        except Exception as e:
            return f"Failed to delete invoice: {str(e)}"

    def record_payment(self, values):
        """Record a payment and mark invoice as paid."""
        try:
            invoice_id = values.get("Invoice")
            if invoice_id:
                invoice_id = int(invoice_id)
            amount = float(values.get("Amount", 0))
            payment_date = self._ui_date_to_db(values.get("Payment Date", "")) or None

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
                mark_invoice_paid=True
            )
            return True if payment_id else "Failed to record payment."
        except Exception as e:
            return f"Failed to record payment: {str(e)}"
# ============================= ^ Finance Manager functions ^ =====================================

# ============================= v Homepage UI Content v =====================================
    def load_homepage_content(self, home_page):
        """Load Finance Manager-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)

        container = pe.ScrollableContainer(parent=home_page, hide_scrollbar_when_loading=True)

        # Row 1: summary full-width
        row1 = pe.RowContainer(parent=container)
        self.load_summary_content(row1, side="top")

        # Row 2: payments (left) + invoices (right)
        row2 = pe.RowContainer(parent=container)
        self.load_payments_content(row2, side="left")
        self.load_invoice_content(row2, side="left")

    def load_summary_content(self, row, side="left"):
        summary_card = pe.FunctionCard(row, "Financial Summary", side=side, pady=6, padx=8)

        # Top info row: late-invoice badge (left) + location selector (right)
        info_row = ctk.CTkFrame(summary_card, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 6))

        late_badge = pe.InfoBadge(info_row, "Late invoices: 0")

        location_dropdown = pe.LocationDropdownWithLabel(info_row)

        # Stat grid
        stats = pe.StatsGrid(summary_card)

        invoiced_value = pe.StatCard(stats, "Invoiced", "£0.00")
        collected_value = pe.StatCard(stats, "Collected", "£0.00")
        outstanding_value = pe.StatCard(stats, "Outstanding", "£0.00")

        def update_summary():
            try:
                location = pe.normalize_location_value(location_dropdown.get())
                summary = self.generate_financial_reports(location)
                invoiced_value.configure(text=f"£{summary['total_invoiced']:,.2f}")
                collected_value.configure(text=f"£{summary['total_collected']:,.2f}")
                outstanding_value.configure(text=f"£{summary['outstanding']:,.2f}")
                late_badge.configure(text=f"Late invoices: {summary['late_invoice_count']}")
            except Exception as e:
                late_badge.configure(text=f"Error: {str(e)}", text_color="red")

        # Enhanced stats and analysis generators for comprehensive export
        def generate_detailed_stats(location=None):
            loc = pe.normalize_location_value(location) if location else "all"
            summary = invoices_repo.get_financial_summary(loc)
            loc_label = location if location and location != "All Locations" else "All Locations"
            collection_rate = (summary['total_collected'] / summary['total_invoiced'] * 100) if summary['total_invoiced'] > 0 else 0
            return (
                f"Location: {loc_label}\n\n"
                f"Total Invoiced: £{summary['total_invoiced']:,.2f}\n\n"
                f"Total Collected: £{summary['total_collected']:,.2f}\n\n"
                f"Outstanding: £{summary['outstanding']:,.2f}\n\n"
                f"Late Invoices: {summary['late_invoice_count']}\n\n"
                f"Collection Rate: {collection_rate:.1f}%"
            )
        
        def generate_financial_analysis(location=None):
            loc = pe.normalize_location_value(location) if location else "all"
            summary = invoices_repo.get_financial_summary(loc)
            loc_label = location if location and location != "All Locations" else "All Locations"
            collection_rate = (summary['total_collected'] / summary['total_invoiced'] * 100) if summary['total_invoiced'] > 0 else 0
            outstanding_rate = (summary['outstanding'] / summary['total_invoiced'] * 100) if summary['total_invoiced'] > 0 else 0
            return (
                f"Location: {loc_label}\n\n"
                f"Total Invoiced: £{summary['total_invoiced']:,.2f}\n\n"
                f"Collected: £{summary['total_collected']:,.2f}\n\n"
                f"Outstanding: £{summary['outstanding']:,.2f}\n\n"
                f"Collection Rate: {collection_rate:.1f}%\n\n"
                f"Outstanding Rate: {outstanding_rate:.1f}%\n\n"
                f"Late Invoices: {summary['late_invoice_count']}\n\n"
                f"Financial Health: {'Excellent' if collection_rate >= 90 else 'Good' if collection_rate >= 75 else 'Fair' if collection_rate >= 60 else 'Needs Attention'}"
            )

        def create_financial_pie(location=None):
            loc = pe.normalize_location_value(location) if location else "all"
            return FinanceGraphService.create_financial_status_pie_chart(loc)
        
        def create_financial_bar(location=None):
            loc = pe.normalize_location_value(location) if location else "all"
            return FinanceGraphService.create_financial_comparison_bar_chart(loc)

        # Graph popup with comprehensive export enabled
        button, export_btn = pe.GraphPopup().open_graph_popup(
            summary_card,
            popup_title="Finance Trends Graph",
            button_text="View Graphs",
            graph_function=FinanceGraphService.create_collected_trend_graph,
            default_location=lambda: location_dropdown.get() or "All Locations",
            get_date_range_func=lambda location_str, grouping: invoices_repo.get_finance_date_range(
                pe.normalize_location_value(location_str), grouping=grouping
            ),
            location_mapper=pe.normalize_location_value,
            stats_generator=generate_detailed_stats,
            export_title="Financial Analysis Report",
            export_filename="financial_analysis_report",
            pie_chart_generator=create_financial_pie,
            bar_chart_generator=create_financial_bar,
            bar_text_generator=generate_financial_analysis
        )

        # Auto-refresh summary on location change (debounced)
        refresh_timer, schedule_refresh = pe.create_debounced_refresh(summary_card, update_summary)
        location_dropdown.configure(command=schedule_refresh)
        update_summary()

    def load_invoice_content(self, row, side="left"):
        invoices_card = pe.FunctionCard(row, "Manage Invoices", side=side, pady=6, padx=8)

        def format_tenants(tenant):
            display = f"ID {tenant['tenant_ID']}: {tenant['first_name']} {tenant['last_name']}"
            return (display, tenant['tenant_ID'])

        fields = [
            {"name": "Tenant", "type": "dropdown", "subtype": "dynamic", 'options': {
                    'data_fetcher': get_all_tenant_names,
                    'display_formatter': format_tenants,
                    'empty_message': 'No tenants available'
                }, "required": True},
            {"name": "Amount Due", "type": "text", "subtype": "currency", "required": True, "placeholder": "£0.00"},
            {"name": "Due Date", "type": "text", "subtype": "date", "placeholder": "YYYY-MM-DD", "required": True},
            {"name": "Issue Date", "type": "text", "subtype": "date", "placeholder": "YYYY-MM-DD", "required": False},
        ]
        pe.Form(
            invoices_card,
            fields,
            name="",
            submit_text="Create invoice",
            on_submit=self.create_invoice
        )

        # Edit invoices popup
        button, open_popup = pe.PopupCard(
            invoices_card,
            title="Invoices",
            button_text="View / Edit Invoices",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(button, font_size=15)

        def setup_popup():
            content = open_popup()

            columns = [
                {"name": "ID", "key": "invoice_ID", "width": 40, "editable": False},
                {"name": "Tenant ID", "key": "tenant_ID", "width": 80, "format": "number"},
                {"name": "Tenant", "key": "tenant_name", "width": 120, "editable": False},
                {"name": "City", "key": "city", "width": 90, "editable": False},
                {"name": "Amount", "key": "amount_due", "width": 80, "format": "currency"},
                {"name": "Due Date", "key": "due_date", "width": 100, "format": "date"},
                {"name": "Issue Date", "key": "issue_date", "width": 100, "format": "date"},
                {"name": "Paid", "key": "paid", "width": 70, "format": "boolean", "options": ["Paid", "Unpaid"]},
            ]

            def get_data(location):
                try:
                    return invoices_repo.get_invoices(location)
                except Exception as e:
                    print(f"Error loading invoices: {e}")
                    return []

            pe.EditableTablePopup(
                content,
                columns,
                get_data_func=get_data,
                on_delete_func=self.delete_invoice_row,
                on_update_func=self.update_invoice_row,
                include_location_filter=True,
                location_mapper=pe.normalize_location_value
            )

        button.configure(command=setup_popup)

    def load_payments_content(self, row, side="top"):
        payments_card = pe.FunctionCard(row, "Payments", side=side, pady=6, padx=8)

        # Define data fetcher and formatter for unpaid invoices
        def fetch_unpaid_invoices():
            location = self.location if self.location else "all"
            return invoices_repo.get_invoices(location=location, paid=0)

        def format_invoice(inv):
            display = f"Invoice #{inv['invoice_ID']} - {inv['tenant_name']} - £{inv['amount_due']:.2f} (Due: {inv['due_date']})"
            return (display, inv['invoice_ID'])

        fields = [
            {
                "name": "Invoice",
                "type": "dropdown",
                "subtype": "dynamic",
                "required": True,
                "options": {
                    'data_fetcher': fetch_unpaid_invoices,
                    'display_formatter': format_invoice,
                    'empty_message': 'No unpaid invoices'
                }
            },
            {"name": "Amount", "type": "text", "subtype": "currency", "required": True, "placeholder": "£0.00"},
            {"name": "Payment Date", "type": "text", "subtype": "date", "placeholder": "YYYY-MM-DD", "required": False}
        ]
        pe.Form(
            payments_card,
            fields,
            name="",
            submit_text="Record Payment",
            on_submit=self.record_payment
        )

        actions = ctk.CTkFrame(payments_card, fg_color="transparent")
        actions.pack(fill="x", pady=(2, 0))

        # Two-column action row
        actions_left = ctk.CTkFrame(actions, fg_color="transparent")
        actions_left.pack(side="left", fill="x", expand=True, padx=(0, 6))

        actions_right = ctk.CTkFrame(actions, fg_color="transparent")
        actions_right.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # View payments popup
        pay_btn, open_pay_popup = pe.PopupCard(
            actions_left,
            title="Payments",
            button_text="View Payments",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(pay_btn, font_size=15)

        # View late invoices popup
        late_btn, open_late_popup = pe.PopupCard(
            actions_right,
            title="Late / Unpaid Invoices",
            button_text="Late Invoices",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(late_btn, font_size=15)

        def setup_payments_popup():
            content = open_pay_popup()

            columns = [
                {"name": "ID", "key": "payment_ID", "width": 80, "editable": False},
                {"name": "Invoice ID", "key": "invoice_ID", "width": 100, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 220, "editable": False},
                {"name": "City", "key": "city", "width": 160, "editable": False},
                {"name": "Payment Date", "key": "payment_date", "width": 130, "editable": False, "format": "date"},
                {"name": "Amount", "key": "amount", "width": 120, "editable": False, "format": "currency"},
            ]

            def get_data(location):
                return payments_repo.get_payments(location)

            pe.ViewableTablePopup(
                content,
                columns,
                get_data_func=get_data,
                include_location_filter=True,
                location_mapper=pe.normalize_location_value,
            )

        def setup_late_popup():
            content = open_late_popup()

            columns = [
                {"name": "ID", "key": "invoice_ID", "width": 80, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 220, "editable": False},
                {"name": "City", "key": "city", "width": 160, "editable": False},
                {"name": "Amount", "key": "amount_due", "width": 120, "editable": False, "format": "currency"},
                {"name": "Due Date", "key": "due_date", "width": 120, "editable": False, "format": "date"},
                {"name": "Issue Date", "key": "issue_date", "width": 120, "editable": False, "format": "date"},
                {"name": "Days Late", "key": "days_late", "width": 100, "editable": False, "format": "number"},
            ]

            def get_data(location):
                return invoices_repo.get_late_invoices(location)

            pe.ViewableTablePopup(
                content,
                columns,
                get_data_func=get_data,
                include_location_filter=True,
                location_mapper=pe.normalize_location_value,
            )

        pay_btn.configure(command=setup_payments_popup)
        late_btn.configure(command=setup_late_popup)

# ============================= ^ Homepage UI Content ^ =====================================
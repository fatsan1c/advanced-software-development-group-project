import customtkinter as ctk
import pages.components.page_elements as pe
import pages.components.input_validation as input_validation
import database_operations.repos.finance_repository as finance_repo
from models.user import User

try:
    from tkcalendar import Calendar
except Exception:
    Calendar = None


class FinanceManager(User):
    """Finance manager with financial reporting and payment processing capabilities."""
    
    def __init__(self, username: str, location: str = None):
        super().__init__(username, role="Finance Manager", location=location)

# ============================= v Finance Manager functions v  =====================================
    def _selected_location(self, dropdown_value: str | None) -> str:
        """Map UI dropdown value to repository location parameter."""
        if dropdown_value == "All Locations":
            return "all"
        return dropdown_value or "all"

    def generate_financial_reports(self, location: str = "all"):
        """Return financial summary data (used by the dashboard)."""
        return finance_repo.get_financial_summary(location)

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
            tenant_id = int(values.get("Tenant ID", 0))
            amount_due = float(values.get("Amount Due", 0))
            due_date = self._ui_date_to_db(values.get("Due Date", ""))
            issue_date = self._ui_date_to_db(values.get("Issue Date", "")) or None

            if not tenant_id:
                return "Tenant ID is required."
            if not due_date:
                return "Due Date is required (YYYY-MM-DD)."
            if amount_due <= 0:
                return "Amount Due must be greater than 0."

            invoice_id = finance_repo.create_invoice(
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

            success = finance_repo.update_invoice(invoice_id, **kwargs)
            return True if success else "Update failed."
        except Exception as e:
            return f"Failed to update invoice: {str(e)}"

    def delete_invoice_row(self, row_data):
        """Delete an invoice row from the table."""
        try:
            invoice_id = int(row_data.get("invoice_ID"))
            success = finance_repo.delete_invoice(invoice_id)
            return True if success else "Delete failed."
        except Exception as e:
            return f"Failed to delete invoice: {str(e)}"

    def record_payment(self, values):
        """Record a payment and mark invoice as paid."""
        try:
            invoice_id = int(values.get("Invoice ID", 0))
            tenant_id = int(values.get("Tenant ID", 0))
            amount = float(values.get("Amount", 0))
            payment_date = self._ui_date_to_db(values.get("Payment Date", "")) or None

            if not invoice_id:
                return "Invoice ID is required."
            if not tenant_id:
                return "Tenant ID is required."
            if amount <= 0:
                return "Amount must be greater than 0."

            invoice = finance_repo.get_invoice_by_id(invoice_id)
            if not invoice:
                return f"Invoice ID {invoice_id} does not exist."
            if int(invoice.get("tenant_ID")) != tenant_id:
                return f"Invoice {invoice_id} belongs to tenant ID {invoice.get('tenant_ID')}, not {tenant_id}."
            if int(invoice.get("paid") or 0) == 1:
                return f"Invoice {invoice_id} is already marked as paid."

            payment_id = finance_repo.record_payment(
                invoice_id=invoice_id,
                tenant_id=tenant_id,
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

        container = pe.scrollable_container(parent=home_page)

        # Row 1: summary full-width
        row1 = pe.row_container(parent=container)
        self.load_summary_content(row1, side="top")

        # Row 2: payments (left) + invoices (right)
        row2 = pe.row_container(parent=container)
        self.load_payments_content(row2, side="left")
        self.load_invoice_content(row2, side="left")

    def load_summary_content(self, row, side="left"):
        summary_card = pe.function_card(row, "Financial Summary", side=side, pady=6, padx=8)

        # Top info row: late-invoice badge (left) + location selector (right)
        info_row = ctk.CTkFrame(summary_card, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 6))

        late_badge = pe.info_badge(info_row, "Late invoices: 0")

        location_dropdown = pe.location_dropdown_with_label(info_row)

        # Stat grid
        stats = pe.stats_grid(summary_card)

        invoiced_value = pe.stat_card(stats, "Invoiced", "£0.00")
        collected_value = pe.stat_card(stats, "Collected", "£0.00")
        outstanding_value = pe.stat_card(stats, "Outstanding", "£0.00")

        def update_summary():
            try:
                location = self._selected_location(location_dropdown.get())
                summary = self.generate_financial_reports(location)
                invoiced_value.configure(text=f"£{summary['total_invoiced']:,.2f}")
                collected_value.configure(text=f"£{summary['total_collected']:,.2f}")
                outstanding_value.configure(text=f"£{summary['outstanding']:,.2f}")
                late_badge.configure(text=f"Late invoices: {summary['late_invoice_count']}")
            except Exception as e:
                late_badge.configure(text=f"Error: {str(e)}", text_color="red")

        # Replace View Summary with a graph popup (summary still auto-refreshes on dropdown change)
        button, open_popup = pe.popup_card(
            summary_card,
            title="Finance Trends Graph",
            button_text="View Graphs",
            small=False,
            button_size="medium"
        )
        pe.style_primary_button(button, font_size=16)

        def setup_graph_popup():
            content = open_popup()
            
            # Helper to get date range with location parameter
            def get_date_range_wrapper(location_str, grouping):
                location = self._selected_location(location_str)
                return finance_repo.get_finance_date_range(location, grouping=grouping)
            
            # Create standardized graph controls
            controls = pe.create_graph_popup_controls(
                content,
                include_location=True,
                default_location=location_dropdown.get() or "All Locations",
                get_date_range_func=get_date_range_wrapper,
                date_range_params=location_dropdown.get() or "All Locations"
            )
            
            # Setup complete graph with automatic rendering and event bindings
            pe.setup_complete_graph_popup(
                controls,
                content,
                finance_repo.create_collected_trend_graph,
                location_mapper=self._selected_location
            )

        button.configure(command=setup_graph_popup)

        # Auto-refresh summary on location change (debounced)
        refresh_timer, schedule_refresh = pe.create_debounced_refresh(summary_card, update_summary)
        location_dropdown.configure(command=schedule_refresh)
        update_summary()

    def load_invoice_content(self, row, side="left"):
        invoices_card = pe.function_card(row, "Manage Invoices", side=side, pady=6, padx=8)

        fields = [
            {"name": "Tenant ID", "type": "text", "subtype": "number", "required": True},
            {"name": "Amount Due", "type": "text", "subtype": "currency", "required": True, "placeholder": "£0.00"},
            {"name": "Due Date", "type": "text", "subtype": "date", "placeholder": "YYYY-MM-DD", "required": True},
            {"name": "Issue Date", "type": "text", "subtype": "date", "placeholder": "YYYY-MM-DD", "required": False},
        ]
        pe.form_element(
            invoices_card,
            fields,
            name="",
            submit_text="Create invoice",
            on_submit=self.create_invoice
        )

        # Edit invoices popup
        button, open_popup = pe.popup_card(
            invoices_card,
            title="Invoices",
            button_text="View / Edit Invoices",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(button, font_size=15)

        def setup_popup():
            content = open_popup()

            # Filter dropdown
            header, location_dropdown = pe.create_popup_header_with_location(content)

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

            def get_data():
                try:
                    location = self._selected_location(location_dropdown.get())
                    return finance_repo.get_invoices(location)
                except Exception as e:
                    print(f"Error loading invoices: {e}")
                    return []

            _, refresh_table = pe.data_table(
                content,
                columns,
                editable=True,
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_invoice_row,
                on_update=self.update_invoice_row,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10,
                scrollable=False
            )

            # Top refresh button next to the dropdown
            pe.create_refresh_button(header, refresh_table)

            # Optional: auto-refresh when changing city
            def refresh_with_reset():
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_table()
            
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, refresh_with_reset)
            location_dropdown.configure(command=schedule_refresh)

        button.configure(command=setup_popup)

    def load_payments_content(self, row, side="top"):
        payments_card = pe.function_card(row, "Payments", side=side, pady=6, padx=8)

        fields = [
            {"name": "Invoice ID", "type": "text", "subtype": "number", "required": True},
            {"name": "Tenant ID", "type": "text", "subtype": "number", "required": True},
            {"name": "Amount", "type": "text", "subtype": "currency", "required": True, "placeholder": "£0.00"},
            {"name": "Payment Date", "type": "text", "subtype": "date", "placeholder": "YYYY-MM-DD", "required": False}
        ]
        pe.form_element(
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
        pay_btn, open_pay_popup = pe.popup_card(
            actions_left,
            title="Payments",
            button_text="View Payments",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(pay_btn, font_size=15)

        # View late invoices popup
        late_btn, open_late_popup = pe.popup_card(
            actions_right,
            title="Late / Unpaid Invoices",
            button_text="Late Invoices",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(late_btn, font_size=15)

        def setup_payments_popup():
            content = open_pay_popup()

            header, location_dropdown = pe.create_popup_header_with_location(content)

            columns = [
                {"name": "ID", "key": "payment_ID", "width": 80, "editable": False},
                {"name": "Invoice ID", "key": "invoice_ID", "width": 100, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 220, "editable": False},
                {"name": "City", "key": "city", "width": 160, "editable": False},
                {"name": "Payment Date", "key": "payment_date", "width": 130, "editable": False, "format": "date"},
                {"name": "Amount", "key": "amount", "width": 120, "editable": False, "format": "currency"},
            ]

            def get_data():
                location = self._selected_location(location_dropdown.get())
                return finance_repo.get_payments(location)

            _, refresh_table = pe.data_table(
                content,
                columns,
                editable=False,
                deletable=False,
                refresh_data=get_data,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10
            )

            pe.create_refresh_button(header, refresh_table)

            def refresh_with_reset():
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_table()
            
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, refresh_with_reset)
            location_dropdown.configure(command=schedule_refresh)

        def setup_late_popup():
            content = open_late_popup()

            header, location_dropdown = pe.create_popup_header_with_location(content)

            columns = [
                {"name": "ID", "key": "invoice_ID", "width": 80, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 220, "editable": False},
                {"name": "City", "key": "city", "width": 160, "editable": False},
                {"name": "Amount", "key": "amount_due", "width": 120, "editable": False, "format": "currency"},
                {"name": "Due Date", "key": "due_date", "width": 120, "editable": False, "format": "date"},
                {"name": "Issue Date", "key": "issue_date", "width": 120, "editable": False, "format": "date"},
                {"name": "Days Late", "key": "days_late", "width": 100, "editable": False, "format": "number"},
            ]

            def get_data():
                location = self._selected_location(location_dropdown.get())
                return finance_repo.get_late_invoices(location)

            _, refresh_table = pe.data_table(
                content,
                columns,
                editable=False,
                deletable=False,
                refresh_data=get_data,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10
            )

            pe.create_refresh_button(header, refresh_table)

            def refresh_with_reset():
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_table()
            
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, refresh_with_reset)
            location_dropdown.configure(command=schedule_refresh)

        pay_btn.configure(command=setup_payments_popup)
        late_btn.configure(command=setup_late_popup)

# ============================= ^ Homepage UI Content ^ =====================================
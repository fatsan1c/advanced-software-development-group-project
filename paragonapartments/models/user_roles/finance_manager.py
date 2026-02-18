import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.finance_repository as finance_repo
import database_operations.repos.location_repository as location_repo
from models.user import User


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

    def create_invoice(self, values):
        """Create a new invoice."""
        try:
            tenant_id = int(values.get("Tenant ID", 0))
            amount_due = float(values.get("Amount Due", 0))
            due_date = values.get("Due Date", "")
            issue_date = values.get("Issue Date", "") or None

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
                kwargs["due_date"] = updated_data["due_date"]
            if "issue_date" in updated_data:
                kwargs["issue_date"] = updated_data["issue_date"]
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
            payment_date = values.get("Payment Date", "") or None

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

        # Row 1
        row1 = pe.row_container(parent=container)
        self.load_summary_content(row1)
        self.load_invoice_content(row1)

        # Row 2
        row2 = pe.row_container(parent=container)
        self.load_late_payments_content(row2)
        self.load_payment_content(row2)

        # Row 3
        row3 = pe.row_container(parent=container)
        self.load_payments_table_content(row3)

    def load_summary_content(self, row):
        summary_card = pe.function_card(row, "Financial Summary", side="left")

        cities = ["All Locations"] + location_repo.get_all_cities()
        location_dropdown = ctk.CTkComboBox(
            summary_card,
            values=cities,
            width=200,
            font=("Arial", 14)
        )
        location_dropdown.set("All Locations")
        location_dropdown.pack(pady=10, padx=20)

        result_label = ctk.CTkLabel(
            summary_card,
            text="",
            font=("Arial", 16, "bold"),
            text_color="#3B8ED0"
        )
        result_label.pack(pady=10, padx=20)

        def update_summary():
            location = self._selected_location(location_dropdown.get())
            summary = self.generate_financial_reports(location)
            result_label.configure(
                text=(
                    f"Invoiced: £{summary['total_invoiced']:,.2f} | "
                    f"Collected: £{summary['total_collected']:,.2f} | "
                    f"Outstanding: £{summary['outstanding']:,.2f}\n"
                    f"Late invoices: {summary['late_invoice_count']}"
                )
            )

        # Replace View Summary with a graph popup (summary still auto-refreshes on dropdown change)
        button, open_popup = pe.popup_card(
            summary_card,
            title="Financial Summary Graph",
            button_text="View Graphs",
            small=False,
            button_size="medium"
        )

        def setup_graph_popup():
            content = open_popup()
            location = self._selected_location(location_dropdown.get())
            finance_repo.create_financial_summary_graph(content, location)

        button.configure(command=setup_graph_popup)

        # Auto-refresh summary on location change (debounced, like other finance dropdowns)
        refresh_timer = {"id": None}
        def schedule_refresh(_choice=None):
            if refresh_timer["id"] is not None:
                try:
                    summary_card.after_cancel(refresh_timer["id"])
                except Exception:
                    pass
            refresh_timer["id"] = summary_card.after(150, update_summary)

        location_dropdown.configure(command=schedule_refresh)
        update_summary()

    def load_invoice_content(self, row):
        invoices_card = pe.function_card(row, "Manage Invoices", side="left")

        # Create invoice form
        fields = [
            {"name": "Tenant ID", "type": "text", "subtype": "number", "required": True},
            {"name": "Amount Due", "type": "text", "subtype": "currency", "required": True},
            {"name": "Due Date", "type": "text", "subtype": "date", "required": True},
            {"name": "Issue Date", "type": "text", "subtype": "date", "required": False},
        ]
        pe.form_element(invoices_card, fields, name="Create Invoice", submit_text="Create", on_submit=self.create_invoice, small=True)

        # Edit invoices popup
        button, open_popup = pe.popup_card(
            invoices_card,
            title="Invoices",
            button_text="View / Edit Invoices",
            small=False,
            button_size="small"
        )

        def setup_popup():
            content = open_popup()

            # Filter dropdown
            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

            cities = ["All Locations"] + location_repo.get_all_cities()
            location_dropdown = ctk.CTkComboBox(header, values=cities, width=220, font=("Arial", 13))
            location_dropdown.set("All Locations")
            location_dropdown.pack(side="left")

            columns = [
                {"name": "ID", "key": "invoice_ID", "width": 40, "editable": False},
                {"name": "Tenant ID", "key": "tenant_ID", "width": 80},
                {"name": "Tenant", "key": "tenant_name", "width": 120, "editable": False},
                {"name": "City", "key": "city", "width": 90, "editable": False},
                {"name": "Amount", "key": "amount_due", "width": 80, "format": "currency"},
                {"name": "Due Date", "key": "due_date", "width": 100},
                {"name": "Issue Date", "key": "issue_date", "width": 100},
                {"name": "Paid (0/1)", "key": "paid", "width": 70},
            ]

            def get_data():
                location = self._selected_location(location_dropdown.get())
                return finance_repo.get_invoices(location)

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
                page_size=10
            )

            # Top refresh button next to the dropdown
            ctk.CTkButton(
                header,
                text="⟳ Refresh",
                command=refresh_table,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25")
            ).pack(side="left", padx=(12, 0))

            # Optional: auto-refresh when changing city
            refresh_timer = {"id": None}
            def schedule_refresh(_choice=None):
                if refresh_timer["id"] is not None:
                    try:
                        content.after_cancel(refresh_timer["id"])
                    except Exception:
                        pass
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_timer["id"] = content.after(150, refresh_table)

            location_dropdown.configure(command=schedule_refresh)

        button.configure(command=setup_popup)

    def load_late_payments_content(self, row):
        late_card = pe.function_card(row, "Late Payments", side="left")

        button, open_popup = pe.popup_card(
            late_card,
            title="Late / Unpaid Invoices",
            button_text="View Late Invoices",
            small=False,
            button_size="medium"
        )

        def setup_popup():
            content = open_popup()

            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))
            ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

            cities = ["All Locations"] + location_repo.get_all_cities()
            location_dropdown = ctk.CTkComboBox(header, values=cities, width=220, font=("Arial", 13))
            location_dropdown.set("All Locations")
            location_dropdown.pack(side="left")

            columns = [
                {"name": "ID", "key": "invoice_ID", "width": 80, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 220, "editable": False},
                {"name": "City", "key": "city", "width": 160, "editable": False},
                {"name": "Amount", "key": "amount_due", "width": 120, "editable": False, "format": "currency"},
                {"name": "Due Date", "key": "due_date", "width": 120, "editable": False},
                {"name": "Issue Date", "key": "issue_date", "width": 120, "editable": False}
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

            ctk.CTkButton(
                header,
                text="⟳ Refresh",
                command=refresh_table,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25")
            ).pack(side="left", padx=(12, 0))

            refresh_timer = {"id": None}
            def schedule_refresh(_choice=None):
                if refresh_timer["id"] is not None:
                    try:
                        content.after_cancel(refresh_timer["id"])
                    except Exception:
                        pass
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_timer["id"] = content.after(150, refresh_table)

            location_dropdown.configure(command=schedule_refresh)

        button.configure(command=setup_popup)

    def load_payment_content(self, row):
        payment_card = pe.function_card(row, "Record Payment", side="left")

        fields = [
            {"name": "Invoice ID", "type": "text", "subtype": "number", "required": True},
            {"name": "Tenant ID", "type": "text", "subtype": "number", "required": True},
            {"name": "Amount", "type": "text", "subtype": "currency", "required": True},
            {"name": "Payment Date", "type": "text", "subtype": "date", "required": False}
        ]
        pe.form_element(payment_card, fields, name="Payment", submit_text="Record Payment", on_submit=self.record_payment, small=True)

    def load_payments_table_content(self, row):
        payments_card = pe.function_card(row, "Payments", side="top")

        button, open_popup = pe.popup_card(
            payments_card,
            title="Payments",
            button_text="View Payments",
            small=False,
            button_size="medium"
        )

        def setup_popup():
            content = open_popup()

            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

            cities = ["All Locations"] + location_repo.get_all_cities()
            location_dropdown = ctk.CTkComboBox(header, values=cities, width=220, font=("Arial", 13))
            location_dropdown.set("All Locations")
            location_dropdown.pack(side="left")

            columns = [
                {"name": "ID", "key": "payment_ID", "width": 80, "editable": False},
                {"name": "Invoice ID", "key": "invoice_ID", "width": 100, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 220, "editable": False},
                {"name": "City", "key": "city", "width": 160, "editable": False},
                {"name": "Payment Date", "key": "payment_date", "width": 130, "editable": False},
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

            ctk.CTkButton(
                header,
                text="⟳ Refresh",
                command=refresh_table,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25")
            ).pack(side="left", padx=(12, 0))

            refresh_timer = {"id": None}
            def schedule_refresh(_choice=None):
                if refresh_timer["id"] is not None:
                    try:
                        content.after_cancel(refresh_timer["id"])
                    except Exception:
                        pass
                # Reset to page 1 whenever filter changes
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_timer["id"] = content.after(150, refresh_table)

            location_dropdown.configure(command=schedule_refresh)

        button.configure(command=setup_popup)
# ============================= ^ Homepage UI Content ^ =====================================
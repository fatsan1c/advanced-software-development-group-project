import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.finance_repository as finance_repo
import database_operations.repos.location_repository as location_repo
from models.user import User
from datetime import datetime
from config.theme import PRIMARY_BLUE, PRIMARY_BLUE_HOVER, ROUND_BOX, ROUND_BTN, ROUND_INPUT

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
        Validate and normalize UI date string (YYYY-MM-DD format).
        Returns None for blank values.
        """
        if date_str is None:
            return None
        s = str(date_str).strip()
        if not s:
            return None
        try:
            # Validate format by parsing
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except Exception as e:
            raise ValueError(f"Invalid date '{date_str}'. Expected YYYY-MM-DD.") from e

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
            # Controls
            controls = ctk.CTkFrame(content, fg_color="transparent")
            controls.pack(fill="x", padx=10, pady=(5, 10))

            row_top = ctk.CTkFrame(controls, fg_color="transparent")
            row_top.pack(fill="x")

            ctk.CTkLabel(row_top, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))
            popup_cities = ["All Locations"] + location_repo.get_all_cities()
            popup_location_dropdown = ctk.CTkComboBox(row_top, values=popup_cities, width=220, font=("Arial", 13))
            popup_location_dropdown.set(location_dropdown.get() or "All Locations")
            popup_location_dropdown.pack(side="left")

            ctk.CTkLabel(row_top, text="Grouping:", font=("Arial", 14, "bold")).pack(side="left", padx=(18, 8))
            grouping_dropdown = ctk.CTkComboBox(row_top, values=["Monthly", "Yearly"], width=140, font=("Arial", 13))
            grouping_dropdown.set("Monthly")
            grouping_dropdown.pack(side="left")

            # Date range row
            row_dates = ctk.CTkFrame(controls, fg_color="transparent")
            row_dates.pack(fill="x", pady=(10, 0))

            # Default date range based on available data (monthly initial view)
            location_for_defaults = self._selected_location(popup_location_dropdown.get())
            default_range = finance_repo.get_finance_date_range(location_for_defaults, grouping="month")
            default_start = default_range.get("start_date", "")
            default_end = default_range.get("end_date", "")

            ctk.CTkLabel(row_dates, text="Start (YYYY-MM-DD):", font=("Arial", 13, "bold")).pack(side="left", padx=(0, 8))
            start_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            start_wrap.pack(side="left")
            start_entry = ctk.CTkEntry(start_wrap, width=140, font=("Arial", 13))
            if default_start:
                start_entry.insert(0, default_start)
            start_entry.pack(side="left")

            ctk.CTkLabel(row_dates, text="End (YYYY-MM-DD):", font=("Arial", 13, "bold")).pack(side="left", padx=(18, 8))
            end_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            end_wrap.pack(side="left")
            end_entry = ctk.CTkEntry(end_wrap, width=140, font=("Arial", 13))
            if default_end:
                end_entry.insert(0, default_end)
            end_entry.pack(side="left")

            ctk.CTkButton(
                start_wrap,
                text="📅",
                width=34,
                height=28,
                font=("Arial", 13),
                command=lambda: pe.open_date_picker(start_entry, content.winfo_toplevel()),
                fg_color=("gray80", "gray25"),
                hover_color=("gray70", "gray30"),
            ).pack(side="left", padx=(6, 0))

            ctk.CTkButton(
                end_wrap,
                text="📅",
                width=34,
                height=28,
                font=("Arial", 13),
                command=lambda: pe.open_date_picker(end_entry, content.winfo_toplevel()),
                fg_color=("gray80", "gray25"),
                hover_color=("gray70", "gray30"),
            ).pack(side="left", padx=(6, 0))

            def apply_grouping_defaults(grouping_value: str):
                gv = (grouping_value or "").strip().lower()
                if gv.startswith("year"):
                    grouping_norm = "year"
                else:
                    grouping_norm = "month"

                location = self._selected_location(popup_location_dropdown.get())
                rng = finance_repo.get_finance_date_range(location, grouping=grouping_norm)
                start_entry.delete(0, "end")
                end_entry.delete(0, "end")
                if rng.get("start_date"):
                    start_entry.insert(0, rng["start_date"])
                if rng.get("end_date"):
                    end_entry.insert(0, rng["end_date"])

            # Error/status label
            error_label = ctk.CTkLabel(
                content,
                text="",
                font=("Arial", 12),
                text_color="red",
                wraplength=900,
                anchor="w",
                justify="left",
            )
            error_label.pack(fill="x", padx=10, pady=(0, 5))

            # Graph container
            graph_container = ctk.CTkFrame(content, fg_color="transparent")
            graph_container.pack(fill="both", expand=True)

            def render_graph():
                # Clear previous graph widgets/canvases
                for w in graph_container.winfo_children():
                    try:
                        w.destroy()
                    except Exception:
                        pass

                try:
                    location = self._selected_location(popup_location_dropdown.get())
                    start_date = start_entry.get().strip() or None
                    end_date = end_entry.get().strip() or None

                    grouping_value = (grouping_dropdown.get() or "Monthly").strip().lower()
                    grouping = "year" if grouping_value.startswith("year") else "month"

                    finance_repo.create_collected_trend_graph(
                        graph_container,
                        location=location,
                        start_date=start_date,
                        end_date=end_date,
                        grouping=grouping,
                    )
                    error_label.configure(text="")
                except Exception as e:
                    error_label.configure(text=str(e))

            refresh_btn = ctk.CTkButton(
                row_top,
                text="⟳ Refresh",
                command=render_graph,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25"),
            )
            refresh_btn.pack(side="left", padx=(18, 0))

            # Auto-refresh when location changes (debounced)
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, render_graph)

            popup_location_dropdown.configure(command=schedule_refresh)
            def on_grouping_change(choice=None):
                apply_grouping_defaults(grouping_dropdown.get())
                schedule_refresh(choice)
            grouping_dropdown.configure(command=on_grouping_change)

            # Initial render
            render_graph()

        button.configure(command=setup_graph_popup)

        # Auto-refresh summary on location change (debounced)
        refresh_timer, schedule_refresh = pe.create_debounced_refresh(summary_card, update_summary)
        location_dropdown.configure(command=schedule_refresh)
        update_summary()

    def load_invoice_content(self, row, side="left"):
        invoices_card = pe.function_card(row, "Manage Invoices", side=side, pady=6, padx=8)

        fields = [
            {"name": "Tenant ID", "type": "text", "subtype": "number", "required": True},
            {"name": "Amount Due", "type": "text", "subtype": "currency", "required": True},
            {"name": "Due Date", "type": "text", "subtype": "date", "placeholder": "Due Date (YYYY-MM-DD)", "required": True},
            {"name": "Issue Date", "type": "text", "subtype": "date", "placeholder": "Issue Date (YYYY-MM-DD)", "required": False},
        ]
        pe.form_element(
            invoices_card,
            fields,
            name="",
            submit_text="Create invoice",
            on_submit=self.create_invoice,
            small=True,
            expand=False,
            fill="x",
            pady=(2, 2),
            submit_button_height=40,
            submit_button_font_size=15,
            input_corner_radius=ROUND_INPUT,
            submit_corner_radius=ROUND_BTN,
            submit_fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
            submit_hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
            submit_text_color=("white", "white"),
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
                {"name": "Tenant ID", "key": "tenant_ID", "width": 80},
                {"name": "Tenant", "key": "tenant_name", "width": 120, "editable": False},
                {"name": "City", "key": "city", "width": 90, "editable": False},
                {"name": "Amount", "key": "amount_due", "width": 80, "format": "currency"},
                {"name": "Due Date", "key": "due_date", "width": 100, "format": "date"},
                {"name": "Issue Date", "key": "issue_date", "width": 100, "format": "date"},
                {"name": "Paid (0/1)", "key": "paid", "width": 70},
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
            {"name": "Amount", "type": "text", "subtype": "currency", "required": True},
            {"name": "Payment Date", "type": "text", "subtype": "date", "placeholder": "Payment Date (YYYY-MM-DD)", "required": False}
        ]
        pe.form_element(
            payments_card,
            fields,
            name="",
            submit_text="Record Payment",
            on_submit=self.record_payment,
            small=True,
            expand=False,
            fill="x",
            pady=(2, 2),
            submit_button_height=40,
            submit_button_font_size=15,
            input_corner_radius=ROUND_INPUT,
            submit_corner_radius=ROUND_BTN,
            submit_fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
            submit_hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
            submit_text_color=("white", "white"),
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

            pe.create_refresh_button(header, refresh_table)

            def refresh_with_reset():
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_table()
            
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, refresh_with_reset)
            location_dropdown.configure(command=schedule_refresh)

        pay_btn.configure(command=setup_payments_popup)
        late_btn.configure(command=setup_late_popup)

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

            header, location_dropdown = pe.create_popup_header_with_location(content)

            columns = [
                {"name": "ID", "key": "invoice_ID", "width": 80, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 220, "editable": False},
                {"name": "City", "key": "city", "width": 160, "editable": False},
                {"name": "Amount", "key": "amount_due", "width": 120, "editable": False, "format": "currency"},
                {"name": "Due Date", "key": "due_date", "width": 120, "editable": False},
                {"name": "Issue Date", "key": "issue_date", "width": 120, "editable": False}
            ]

            def get_data():
                try:
                    location = self._selected_location(location_dropdown.get())
                    return finance_repo.get_late_invoices(location)
                except Exception as e:
                    print(f"Error loading late invoices: {e}")
                    return []

            _, refresh_table = pe.data_table(
                content,
                columns,
                editable=False,
                deletable=False,
                refresh_data=get_data,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10,
                scrollable=False
            )

            pe.create_refresh_button(header, refresh_table)

            def refresh_with_reset():
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_table()
            
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, refresh_with_reset)
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

            header, location_dropdown = pe.create_popup_header_with_location(content)

            columns = [
                {"name": "ID", "key": "payment_ID", "width": 80, "editable": False},
                {"name": "Invoice ID", "key": "invoice_ID", "width": 100, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 220, "editable": False},
                {"name": "City", "key": "city", "width": 160, "editable": False},
                {"name": "Payment Date", "key": "payment_date", "width": 130, "editable": False},
                {"name": "Amount", "key": "amount", "width": 120, "editable": False, "format": "currency"},
            ]

            def get_data():
                try:
                    location = self._selected_location(location_dropdown.get())
                    return finance_repo.get_payments(location)
                except Exception as e:
                    print(f"Error loading payments: {e}")
                    return []

            _, refresh_table = pe.data_table(
                content,
                columns,
                editable=False,
                deletable=False,
                refresh_data=get_data,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10,
                scrollable=False
            )

            pe.create_refresh_button(header, refresh_table)

            def refresh_with_reset():
                # Reset to page 1 whenever filter changes
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_table()
            
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, refresh_with_reset)
            location_dropdown.configure(command=schedule_refresh)

        button.configure(command=setup_popup)
# ============================= ^ Homepage UI Content ^ =====================================
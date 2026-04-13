"""Contributors: Ahmed AlShamy (24045361)

Finance dashboard card builders."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe
from services import FinanceGraphService


def load_finance_summary_card(self, row, side="left"):
    summary_card = pe.FunctionCard(row, "Financial Summary", side=side, pady=6, padx=8)

    info_row = ctk.CTkFrame(summary_card, fg_color="transparent")
    info_row.pack(fill="x", pady=(0, 6))

    late_badge = pe.InfoBadge(info_row, "Late invoices: 0")
    location_dropdown = pe.LocationDropdownWithLabel(info_row)

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

    def generate_detailed_stats(location=None):
        loc = pe.normalize_location_value(location) if location else "all"
        summary = self.generate_financial_reports(loc)
        loc_label = location if location and location != "All Locations" else "All Locations"
        collection_rate = (summary["total_collected"] / summary["total_invoiced"] * 100) if summary["total_invoiced"] > 0 else 0
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
        summary = self.generate_financial_reports(loc)
        loc_label = location if location and location != "All Locations" else "All Locations"
        collection_rate = (summary["total_collected"] / summary["total_invoiced"] * 100) if summary["total_invoiced"] > 0 else 0
        outstanding_rate = (summary["outstanding"] / summary["total_invoiced"] * 100) if summary["total_invoiced"] > 0 else 0
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

    pe.GraphPopup().open_graph_popup(
        summary_card,
        popup_title="Finance Trends Graph",
        button_text="View Graphs",
        graph_function=FinanceGraphService.create_collected_trend_graph,
        default_location=lambda: location_dropdown.get() or "All Locations",
        get_date_range_func=lambda location_str, grouping: self.get_finance_date_range(
            pe.normalize_location_value(location_str), grouping=grouping
        ),
        location_mapper=pe.normalize_location_value,
        stats_generator=generate_detailed_stats,
        export_title="Financial Analysis Report",
        export_filename="financial_analysis_report",
        pie_chart_generator=create_financial_pie,
        bar_chart_generator=create_financial_bar,
        bar_text_generator=generate_financial_analysis,
    )

    refresh_timer, schedule_refresh = pe.create_debounced_refresh(summary_card, update_summary)
    location_dropdown.configure(command=schedule_refresh)
    update_summary()


def load_finance_payments_card(self, row, side="top"):
    payments_card = pe.FunctionCard(row, "Payments", side=side, pady=6, padx=8)

    def fetch_unpaid_invoices():
        location = self.location if self.location else "all"
        return self.get_unpaid_invoices(location)

    def format_invoice(inv):
        display = f"Invoice #{inv['invoice_ID']} - {inv['tenant_name']} - £{inv['amount_due']:.2f} (Due: {inv['due_date']})"
        return (display, inv["invoice_ID"])

    fields = [
        {
            "name": "Invoice",
            "type": "dropdown",
            "subtype": "dynamic",
            "required": True,
            "options": {
                "data_fetcher": fetch_unpaid_invoices,
                "display_formatter": format_invoice,
                "empty_message": "No unpaid invoices",
            },
        },
        {"name": "Amount", "type": "text", "subtype": "currency", "required": True, "placeholder": "£0.00"},
        {"name": "Payment Date", "type": "text", "subtype": "date", "placeholder": "YYYY-MM-DD", "required": False},
    ]
    pe.Form(
        payments_card,
        fields,
        name="",
        submit_text="Record Payment",
        on_submit=self.record_payment,
    )

    actions = ctk.CTkFrame(payments_card, fg_color="transparent")
    actions.pack(fill="x", pady=(2, 0))

    actions_left = ctk.CTkFrame(actions, fg_color="transparent")
    actions_left.pack(side="left", fill="x", expand=True, padx=(0, 6))

    actions_right = ctk.CTkFrame(actions, fg_color="transparent")
    actions_right.pack(side="left", fill="x", expand=True, padx=(6, 0))

    pay_btn, open_pay_popup = pe.PopupCard(
        actions_left,
        title="Payments",
        button_text="View Payments",
        small=False,
        button_size="full",
    )
    pe.style_secondary_button(pay_btn, font_size=15)

    late_btn, open_late_popup = pe.PopupCard(
        actions_right,
        title="Late / Unpaid Invoices",
        button_text="Late Invoices",
        small=False,
        button_size="full",
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
            return self.get_payments(location)

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
            return self.get_late_invoices(location)

        pe.ViewableTablePopup(
            content,
            columns,
            get_data_func=get_data,
            include_location_filter=True,
            location_mapper=pe.normalize_location_value,
        )

    pay_btn.configure(command=setup_payments_popup)
    late_btn.configure(command=setup_late_popup)


def load_finance_invoice_card(self, row, side="left"):
    invoices_card = pe.FunctionCard(row, "Manage Invoices", side=side, pady=6, padx=8)

    def format_tenants(tenant):
        display = f"ID {tenant['tenant_ID']}: {tenant['first_name']} {tenant['last_name']}"
        return (display, tenant["tenant_ID"])

    fields = [
        {
            "name": "Tenant",
            "type": "dropdown",
            "subtype": "dynamic",
            "options": {
                "data_fetcher": self.get_all_tenant_names,
                "display_formatter": format_tenants,
                "empty_message": "No tenants available",
            },
            "required": True,
        },
        {"name": "Amount Due", "type": "text", "subtype": "currency", "required": True, "placeholder": "£0.00"},
        {"name": "Due Date", "type": "text", "subtype": "date", "placeholder": "YYYY-MM-DD", "required": True},
        {"name": "Issue Date", "type": "text", "subtype": "date", "placeholder": "YYYY-MM-DD", "required": False},
    ]
    pe.Form(
        invoices_card,
        fields,
        name="",
        submit_text="Create invoice",
        on_submit=self.create_invoice,
    )

    button, open_popup = pe.PopupCard(
        invoices_card,
        title="Invoices",
        button_text="View / Edit Invoices",
        small=False,
        button_size="full",
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
                return self.get_invoices(location)
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
            location_mapper=pe.normalize_location_value,
        )

    button.configure(command=setup_popup)

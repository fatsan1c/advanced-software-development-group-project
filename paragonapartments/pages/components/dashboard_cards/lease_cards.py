"""Contributors: Aaron Antal-Bento (23013693)

Lease-related dashboard card builders."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe
from services import LeaseGraphService


def _pct(part: int | float, whole: int | float) -> float:
    return (part / whole * 100) if whole else 0.0


def load_admin_lease_card(self, row):
    lease_card = pe.FunctionCard(row, f"Lease Agreements - {self.location}", side="left", pady=6, padx=8)

    info_row = ctk.CTkFrame(lease_card, fg_color="transparent")
    info_row.pack(fill="x", pady=(0, 6))

    expiring_badge = pe.InfoBadge(info_row, "Expiring soon: 0")

    stats = pe.StatsGrid(lease_card)

    active_value = pe.StatCard(stats, "Active")
    expired_value = pe.StatCard(stats, "Expired")
    total_value = pe.StatCard(stats, "Total")

    def update_lease_display():
        try:
            lease_stats = self.get_lease_statistics(self.location)
            active_count = lease_stats.get("active_leases", 0)
            expired_count = lease_stats.get("expired_leases", 0)
            total_count = lease_stats.get("total_leases", 0)
            expiring_count = lease_stats.get("expiring_soon", 0)

            active_value.configure(text=str(active_count))
            expired_value.configure(text=str(expired_count))
            total_value.configure(text=str(total_count))
            expiring_badge.configure(text=f"Expiring soon: {expiring_count}")
        except Exception as e:
            print(f"Error loading lease data: {e}")

    update_lease_display()
    refresh_timer, schedule_refresh = pe.create_debounced_refresh(lease_card, update_lease_display)

    def generate_lease_stats():
        stats_data = self.get_lease_statistics(self.location)
        active = stats_data.get("active_leases", 0)
        expired = stats_data.get("expired_leases", 0)
        total = stats_data.get("total_leases", 0)
        expiring = stats_data.get("expiring_soon", 0)
        return (
            f"Location: {self.location}\n\n"
            f"Total Leases: {total}\n\n"
            f"Active: {active} ({_pct(active, total):.1f}% of total)\n\n"
            f"Expired: {expired} ({_pct(expired, total):.1f}% of total)\n\n"
            f"Expiring Soon (30 days): {expiring}"
        )

    def generate_lease_analysis():
        stats_data = self.get_lease_statistics(self.location)
        active = stats_data.get("active_leases", 0)
        expired = stats_data.get("expired_leases", 0)
        expiring = stats_data.get("expiring_soon", 0)
        total = stats_data.get("total_leases", 0)
        return (
            f"Location: {self.location}\n\n"
            f"Active Leases: {active}\n\n"
            f"Expired Leases: {expired}\n\n"
            f"Expiring Soon: {expiring}\n\n"
            f"Total Leases: {total}\n\n"
            f"Renewal Rate Needed: {(expiring / active * 100):.1f}% of active leases" if active > 0 else "N/A"
        )

    pe.GraphPopup().open_graph_popup(
        lease_card,
        popup_title=f"Lease Trends Graph - {self.location}",
        button_text="View Graphs",
        graph_function=LeaseGraphService.create_lease_trend_graph,
        include_location=False,
        get_date_range_func=lambda loc, grouping: self.get_lease_date_range(loc, grouping=grouping),
        date_range_params=self.location,
        fixed_location=self.location,
        stats_generator=generate_lease_stats,
        export_title=f"Lease Analysis - {self.location}",
        export_filename=f"lease_analysis_{self.location.lower().replace(' ', '_')}",
        pie_chart_generator=lambda: LeaseGraphService.create_lease_status_pie_chart(self.location),
        bar_chart_generator=lambda: LeaseGraphService.create_lease_comparison_bar_chart(self.location),
        bar_text_generator=generate_lease_analysis,
    )

    data_button, open_data_popup_func = pe.PopupCard(
        lease_card,
        title=f"View Lease Agreements - {self.location}",
        button_text="View Leases",
        small=False,
        button_size="full",
    )
    pe.style_secondary_button(data_button)
    data_button.pack(pady=(10, 0))

    def setup_data_popup():
        content = open_data_popup_func()

        columns = [
            {"name": "ID", "key": "lease_ID", "width": 50, "editable": False},
            {"name": "Tenant", "key": "tenant_name", "width": 110, "editable": False},
            {"name": "Apartment", "key": "apartment_address", "width": 170, "editable": False},
            {"name": "Location", "key": "city", "width": 80, "editable": False},
            {"name": "Start Date", "key": "start_date", "width": 100, "editable": False},
            {"name": "End Date", "key": "end_date", "width": 100, "editable": False},
            {
                "name": "Monthly Rent",
                "key": "monthly_rent",
                "format": "currency",
                "width": 120,
                "editable": False,
            },
            {
                "name": "Status",
                "key": "active",
                "width": 100,
                "format": "boolean",
                "options": ["Active", "Inactive"],
                "editable": False,
            },
            {
                "name": "Expired",
                "key": "expired",
                "width": 80,
                "format": "boolean",
                "options": ["Yes", "No"],
                "editable": False,
            },
        ]

        def get_data():
            try:
                return self.get_all_leases(self.location)
            except Exception as e:
                print(f"Error loading leases: {e}")
                return []

        pe.ViewableTablePopup(
            content,
            columns,
            get_data_func=get_data,
        )

    data_button.configure(command=setup_data_popup)

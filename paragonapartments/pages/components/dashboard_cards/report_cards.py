"""Reporting dashboard card builders."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe
from services import ApartmentGraphService


def _pct(part: int | float, whole: int | float) -> float:
    return (part / whole * 100) if whole else 0.0


def load_admin_report_card(self, row):
    reports_card = pe.FunctionCard(row, f"Performance Report - {self.location}", side="left", pady=6, padx=8)

    info_row = ctk.CTkFrame(reports_card, fg_color="transparent")
    info_row.pack(fill="x", pady=(0, 6))

    vacant_badge = pe.InfoBadge(info_row, "Vacant units: 0")

    stats = pe.StatsGrid(reports_card)
    actual_value = pe.StatCard(stats, "Actual Revenue", "£0.00")
    potential_value = pe.StatCard(stats, "Potential Revenue", "£0.00")

    def update_performance_display():
        try:
            actual_revenue = self.get_monthly_revenue(self.location)
            potential_revenue = self.get_potential_revenue(self.location)
            total = self.get_total_apartments(self.location)
            occupied = self.view_apartment_occupancy()
            vacant = total - occupied

            actual_value.configure(text=f"£{actual_revenue:,.2f}")
            potential_value.configure(text=f"£{potential_revenue:,.2f}")
            vacant_badge.configure(text=f"Vacant units: {vacant}")
        except Exception as e:
            print(f"Error loading revenue data: {e}")

    update_performance_display()
    refresh_timer, schedule_refresh = pe.create_debounced_refresh(reports_card, update_performance_display)

    def generate_performance_stats():
        actual = self.get_monthly_revenue(self.location)
        potential = self.get_potential_revenue(self.location)
        total = self.get_total_apartments(self.location)
        occupied = self.view_apartment_occupancy()
        vacant = total - occupied
        return (
            f"Location: {self.location}\n\n"
            f"Total Apartments: {total}\n\n"
            f"Occupied: {occupied} ({_pct(occupied, total):.1f}%)\n\n"
            f"Vacant: {vacant} ({_pct(vacant, total):.1f}%)\n\n"
            f"Actual Revenue: £{actual:,.2f}\n\n"
            f"Potential Revenue: £{potential:,.2f}"
        )

    def generate_performance_analysis():
        actual = self.get_monthly_revenue(self.location)
        potential = self.get_potential_revenue(self.location)
        lost = potential - actual
        efficiency = (actual / potential * 100) if potential > 0 else 0
        return (
            f"Location: {self.location}\n\n"
            f"Actual Revenue: £{actual:,.2f}\n\n"
            f"Potential Revenue: £{potential:,.2f}\n\n"
            f"Lost Revenue: £{lost:,.2f}\n\n"
            f"Revenue Efficiency: {efficiency:.1f}%\n\n"
            f"Performance Rating: {'Excellent' if efficiency >= 90 else 'Good' if efficiency >= 75 else 'Fair' if efficiency >= 60 else 'Needs Improvement'}"
        )

    pe.GraphPopup().open_graph_popup(
        reports_card,
        popup_title=f"Performance Report Graph - {self.location}",
        button_text="View Graphs",
        graph_function=ApartmentGraphService.create_revenue_trend_graph,
        include_location=False,
        get_date_range_func=lambda loc, grouping: self.get_lease_date_range(loc, grouping=grouping),
        date_range_params=self.location,
        fixed_location=self.location,
        stats_generator=generate_performance_stats,
        export_title=f"Performance Report - {self.location}",
        export_filename=f"performance_report_{self.location.lower().replace(' ', '_')}",
        pie_chart_generator=lambda: ApartmentGraphService.create_occupancy_pie_chart(self.location),
        bar_chart_generator=lambda: ApartmentGraphService.create_revenue_bar_chart(self.location),
        bar_text_generator=generate_performance_analysis,
    )


def load_manager_report_card(self, row):
    reports_card = pe.FunctionCard(row, "Performance Report", side="top", pady=6, padx=8)

    info_row = ctk.CTkFrame(reports_card, fg_color="transparent")
    info_row.pack(fill="x", pady=(0, 6))

    vacant_badge = pe.InfoBadge(info_row, "Vacant units: 0")
    location_dropdown = pe.LocationDropdownWithLabel(info_row)

    stats = pe.StatsGrid(reports_card)
    actual_value = pe.StatCard(stats, "Actual Revenue", "£0.00")
    potential_value = pe.StatCard(stats, "Potential Revenue", "£0.00")

    def update_performance_display(choice=None):
        location = pe.normalize_location_value(location_dropdown.get())
        actual_revenue = self.get_monthly_revenue(location)
        potential_revenue = self.get_potential_revenue(location)
        total = self.get_total_apartments(location)
        occupied = self.view_apartment_occupancy(location)
        vacant = total - occupied

        actual_value.configure(text=f"£{actual_revenue:,.2f}")
        potential_value.configure(text=f"£{potential_revenue:,.2f}")
        vacant_badge.configure(text=f"Vacant units: {vacant}")

    update_performance_display()
    refresh_timer, schedule_refresh = pe.create_debounced_refresh(reports_card, update_performance_display)
    location_dropdown.configure(command=schedule_refresh)

    def generate_performance_stats(location=None):
        loc = pe.normalize_location_value(location) if location else "all"
        actual = self.get_monthly_revenue(loc)
        potential = self.get_potential_revenue(loc)
        total = self.get_total_apartments(loc)
        occupied = self.view_apartment_occupancy(loc)
        vacant = total - occupied
        loc_label = location if location and location != "All Locations" else "All Locations"
        return (
            f"Location: {loc_label}\n\n"
            f"Total Apartments: {total}\n\n"
            f"Occupied: {occupied} ({_pct(occupied, total):.1f}%)\n\n"
            f"Vacant: {vacant} ({_pct(vacant, total):.1f}%)\n\n"
            f"Actual Revenue: £{actual:,.2f}\n\n"
            f"Potential Revenue: £{potential:,.2f}"
        )

    def generate_performance_analysis(location=None):
        loc = pe.normalize_location_value(location) if location else "all"
        actual = self.get_monthly_revenue(loc)
        potential = self.get_potential_revenue(loc)
        lost = potential - actual
        efficiency = (actual / potential * 100) if potential > 0 else 0
        loc_label = location if location and location != "All Locations" else "All Locations"
        return (
            f"Location: {loc_label}\n\n"
            f"Actual Revenue: £{actual:,.2f}\n\n"
            f"Potential Revenue: £{potential:,.2f}\n\n"
            f"Lost Revenue: £{lost:,.2f}\n\n"
            f"Revenue Efficiency: {efficiency:.1f}%\n\n"
            f"Performance Rating: {'Excellent' if efficiency >= 90 else 'Good' if efficiency >= 75 else 'Fair' if efficiency >= 60 else 'Needs Improvement'}"
        )

    def create_occupancy_pie_report(location=None):
        loc = pe.normalize_location_value(location) if location else "all"
        return ApartmentGraphService.create_occupancy_pie_chart(loc)

    def create_revenue_bar_report(location=None):
        loc = pe.normalize_location_value(location) if location else "all"
        return ApartmentGraphService.create_revenue_bar_chart(loc)

    pe.GraphPopup().open_graph_popup(
        reports_card,
        popup_title="Performance Report Graph",
        button_text="View Graphs",
        graph_function=ApartmentGraphService.create_revenue_trend_graph,
        default_location=lambda: location_dropdown.get() or "All Locations",
        get_date_range_func=lambda loc, grouping: self.get_lease_date_range(loc, grouping=grouping),
        location_mapper=pe.normalize_location_value,
        stats_generator=generate_performance_stats,
        export_title="Performance Analysis Report",
        export_filename="performance_analysis_report",
        pie_chart_generator=create_occupancy_pie_report,
        bar_chart_generator=create_revenue_bar_report,
        bar_text_generator=generate_performance_analysis,
    )

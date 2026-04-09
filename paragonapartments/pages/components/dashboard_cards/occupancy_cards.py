"""Contributors: Aaron Antal-Bento (23013693), Ollie Churchley (23020494)

Occupancy-related dashboard card builders."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe
from services import ApartmentGraphService


def _pct(part: int | float, whole: int | float) -> float:
    return (part / whole * 100) if whole else 0.0


def load_admin_occupancy_card(self, row):
    occupancy_card = pe.FunctionCard(row, f"Apartment Occupancy - {self.location}", side="left", pady=6, padx=8)

    info_row = ctk.CTkFrame(occupancy_card, fg_color="transparent")
    info_row.pack(fill="x", pady=(0, 6))

    occupancy_badge = pe.InfoBadge(info_row, "Total units: 0")

    stats = pe.StatsGrid(occupancy_card)

    occupied_value = pe.StatCard(stats, "Occupied")
    available_value = pe.StatCard(stats, "Available")
    total_value = pe.StatCard(stats, "Total")

    def update_occupancy_display():
        try:
            occupied_count = self.view_apartment_occupancy()
            total_count = self.get_total_apartments(self.location)
            available_count = total_count - occupied_count

            occupied_value.configure(text=str(occupied_count))
            available_value.configure(text=str(available_count))
            total_value.configure(text=str(total_count))
            occupancy_badge.configure(text=f"Total units: {total_count}")
        except Exception as e:
            print(f"Error loading occupancy data: {e}")

    update_occupancy_display()
    refresh_timer, schedule_refresh = pe.create_debounced_refresh(occupancy_card, update_occupancy_display)

    button_container = ctk.CTkFrame(occupancy_card, fg_color="transparent")
    button_container.pack(fill="x", pady=(5, 0))

    def generate_occupancy_stats():
        occupied = self.view_apartment_occupancy()
        total = self.get_total_apartments(self.location)
        vacant = total - occupied
        return (
            f"Location: {self.location}\n\n"
            f"Total Apartments: {total}\n\n"
            f"Occupied: {occupied} ({_pct(occupied, total):.1f}%)\n\n"
            f"Vacant: {vacant} ({_pct(vacant, total):.1f}%)"
        )

    def generate_revenue_analysis():
        actual = self.get_monthly_revenue(self.location)
        potential = self.get_potential_revenue(self.location)
        lost = potential - actual
        efficiency = (actual / potential * 100) if potential > 0 else 0
        lost_pct = (lost / potential * 100) if potential > 0 else 0
        return (
            f"Location: {self.location}\n\n"
            f"Actual Revenue: £{actual:,.2f}\n\n"
            f"Potential Revenue: £{potential:,.2f}\n\n"
            f"Lost Revenue: £{lost:,.2f}\n\n"
            f"Revenue Efficiency: {efficiency:.1f}%\n\n"
            f"Revenue Gap: {lost_pct:.1f}% of potential"
        )

    pe.GraphPopup().open_graph_popup(
        button_container,
        popup_title=f"Apartment Occupancy Graph - {self.location}",
        button_text="View Graphs",
        graph_function=ApartmentGraphService.create_occupancy_trend_graph,
        include_location=False,
        get_date_range_func=lambda loc, grouping: self.get_lease_date_range(loc, grouping=grouping),
        date_range_params=self.location,
        fixed_location=self.location,
        stats_generator=generate_occupancy_stats,
        export_title=f"Occupancy Analysis - {self.location}",
        export_filename=f"occupancy_analysis_{self.location.lower().replace(' ', '_')}",
        pie_chart_generator=lambda: ApartmentGraphService.create_occupancy_pie_chart(self.location),
        bar_chart_generator=lambda: ApartmentGraphService.create_revenue_bar_chart(self.location),
        bar_text_generator=generate_revenue_analysis,
    )


def load_manager_occupancy_card(self, row):
    occupancy_card = pe.FunctionCard(row, "Apartment Occupancy", side="left", pady=6, padx=8)

    info_row = ctk.CTkFrame(occupancy_card, fg_color="transparent")
    info_row.pack(fill="x", pady=(0, 6))

    occupancy_badge = pe.InfoBadge(info_row, "Total units: 0")

    location_dropdown = pe.LocationDropdownWithLabel(info_row)

    stats = pe.StatsGrid(occupancy_card)

    occupied_value = pe.StatCard(stats, "Occupied")
    available_value = pe.StatCard(stats, "Available")
    total_value = pe.StatCard(stats, "Total")

    def update_occupancy_display(choice=None):
        location = pe.normalize_location_value(location_dropdown.get())
        occupied_count = self.view_apartment_occupancy(location)
        total_count = self.get_total_apartments(location)
        available_count = total_count - occupied_count

        occupied_value.configure(text=str(occupied_count))
        available_value.configure(text=str(available_count))
        total_value.configure(text=str(total_count))
        occupancy_badge.configure(text=f"Total units: {total_count}")

    update_occupancy_display()
    refresh_timer, schedule_refresh = pe.create_debounced_refresh(occupancy_card, update_occupancy_display)
    location_dropdown.configure(command=schedule_refresh)

    def generate_occupancy_stats(location=None):
        loc = pe.normalize_location_value(location) if location else "all"
        occupied = self.view_apartment_occupancy(loc)
        total = self.get_total_apartments(loc)
        vacant = total - occupied
        loc_label = location if location and location != "All Locations" else "All Locations"
        return (
            f"Location: {loc_label}\n\n"
            f"Total Apartments: {total}\n\n"
            f"Occupied: {occupied} ({_pct(occupied, total):.1f}%)\n\n"
            f"Vacant: {vacant} ({_pct(vacant, total):.1f}%)"
        )

    def generate_revenue_analysis(location=None):
        loc = pe.normalize_location_value(location) if location else "all"
        actual = self.get_monthly_revenue(loc)
        potential = self.get_potential_revenue(loc)
        lost = potential - actual
        efficiency = (actual / potential * 100) if potential > 0 else 0
        lost_pct = (lost / potential * 100) if potential > 0 else 0
        loc_label = location if location and location != "All Locations" else "All Locations"
        return (
            f"Location: {loc_label}\n\n"
            f"Actual Revenue: £{actual:,.2f}\n\n"
            f"Potential Revenue: £{potential:,.2f}\n\n"
            f"Lost Revenue: £{lost:,.2f}\n\n"
            f"Revenue Efficiency: {efficiency:.1f}%\n\n"
            f"Revenue Gap: {lost_pct:.1f}% of potential"
        )

    def create_occupancy_pie(location=None):
        loc = pe.normalize_location_value(location) if location else "all"
        return ApartmentGraphService.create_occupancy_pie_chart(loc)

    def create_revenue_bar(location=None):
        loc = pe.normalize_location_value(location) if location else "all"
        return ApartmentGraphService.create_revenue_bar_chart(loc)

    pe.GraphPopup().open_graph_popup(
        occupancy_card,
        popup_title="Apartment Occupancy Graph",
        button_text="View Graphs",
        graph_function=ApartmentGraphService.create_occupancy_trend_graph,
        default_location=lambda: location_dropdown.get() or "All Locations",
        get_date_range_func=lambda loc, grouping: self.get_lease_date_range(loc, grouping=grouping),
        location_mapper=pe.normalize_location_value,
        stats_generator=generate_occupancy_stats,
        export_title="Occupancy Analysis Report",
        export_filename="occupancy_analysis_report",
        pie_chart_generator=create_occupancy_pie,
        bar_chart_generator=create_revenue_bar,
        bar_text_generator=generate_revenue_analysis,
    )

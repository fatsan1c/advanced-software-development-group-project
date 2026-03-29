"""Reporting services for chart generation outside repository modules."""

from __future__ import annotations

import numpy as np

from database_operations.database_repositories.apartment_repository import ApartmentsRepository
from database_operations.database_repositories.finance_repository import InvoicesRepository
from database_operations.database_repositories.lease_repository import LeaseAgreementsRepository
from pages.components.chart_utils import (
    BarChart,
    ComparisonBarChart,
    PieChart,
    TrendChart,
)
from pages.components.config.theme import THEME


def _title_location(location) -> str:
    return location if location and str(location).lower() not in {"all", "all locations"} else "All Locations"


class ApartmentGraphService:
    """Chart/report generation for apartment and occupancy visuals."""

    @staticmethod
    def create_occupancy_graph(parent, location=None):
        apartment_repo = ApartmentsRepository()
        occupied_count = apartment_repo.get_all_occupancy(location)
        total_count = apartment_repo.get_total_apartments(location)
        vacant_count = total_count - occupied_count
        title_location = location if location and str(location).lower() != "all" else "All Locations"
        return BarChart.create(
            parent,
            labels=["Occupied", "Vacant"],
            values=[occupied_count, vacant_count],
            colors=[THEME.charts.accent_green, THEME.charts.accent_red],
            title=f"Apartment Occupancy in {title_location}",
            y_label="Number of Apartments",
            value_formatter="count",
            y_padding=0.5,
        )

    @staticmethod
    def create_performance_graph(parent, location=None):
        apartment_repo = ApartmentsRepository()
        actual_revenue = apartment_repo.get_monthly_revenue(location)
        potential_revenue = apartment_repo.get_potential_revenue(location)
        lost_revenue = potential_revenue - actual_revenue
        title_location = _title_location(location)
        return BarChart.create(
            parent,
            labels=["Actual Revenue", "Lost Revenue"],
            values=[actual_revenue, lost_revenue],
            colors=[THEME.charts.accent_green, THEME.charts.accent_orange],
            title=f"Monthly Revenue Performance in {title_location}",
            y_label="Revenue (GBP)",
            value_formatter="currency",
            y_padding=50,
        )

    @staticmethod
    def create_occupancy_trend_graph(parent, location=None, start_date=None, end_date=None, grouping="month"):
        lease_repo = LeaseAgreementsRepository()
        data = lease_repo.get_occupancy_timeseries(
            location=location,
            start_date=start_date,
            end_date=end_date,
            grouping=grouping,
        )
        series_data = data.get("series") or []
        periods = [row.get("period", "") for row in series_data]
        occupied = np.array([float(row.get("occupied") or 0) for row in series_data], dtype=float)
        total = np.array([float(row.get("total") or 0) for row in series_data], dtype=float)
        title_loc = _title_location(location)

        if not series_data:
            return TrendChart.create(
                parent,
                periods=[],
                series=[],
                title=f"Occupancy Trends - {title_loc}",
                y_label="Number of Apartments",
                y_formatter="count",
            )

        return TrendChart.create(
            parent,
            periods=periods,
            series=[
                ("Occupied", occupied, THEME.charts.accent_green),
                ("Total Apartments", total, THEME.charts.accent_blue),
            ],
            title=f"Occupancy Trends - {title_loc}",
            y_label="Number of Apartments",
            y_formatter="count",
            fill_primary=True,
            fill_secondary=True,
            primary_color=THEME.charts.accent_green,
            show_kpi=False,
            show_toolbar=True,
            y_lim_dynamic=True,
        )

    @staticmethod
    def create_revenue_trend_graph(parent, location=None, start_date=None, end_date=None, grouping="month"):
        lease_repo = LeaseAgreementsRepository()
        data = lease_repo.get_revenue_timeseries(
            location=location,
            start_date=start_date,
            end_date=end_date,
            grouping=grouping,
        )
        series_data = data.get("series") or []
        periods = [row.get("period", "") for row in series_data]
        actual = np.array([float(row.get("actual_revenue") or 0) for row in series_data], dtype=float)
        potential = np.array([float(row.get("potential_revenue") or 0) for row in series_data], dtype=float)
        title_loc = _title_location(location)

        if not series_data:
            return TrendChart.create(
                parent,
                periods=[],
                series=[],
                title=f"Revenue Trends - {title_loc}",
                y_label="Revenue (GBP)",
                y_formatter="currency",
            )

        return TrendChart.create(
            parent,
            periods=periods,
            series=[
                ("Actual Revenue", actual, THEME.charts.accent_green),
                ("Potential Revenue", potential, THEME.charts.accent_orange),
            ],
            title=f"Revenue Trends - {title_loc}",
            y_label="Revenue (GBP)",
            y_formatter="currency",
            fill_primary=True,
            fill_secondary=True,
            primary_color=THEME.charts.accent_green,
            show_kpi=False,
            show_toolbar=True,
            y_lim_dynamic=True,
        )

    @staticmethod
    def create_occupancy_pie_chart(location=None):
        apartment_repo = ApartmentsRepository()
        occupied = apartment_repo.get_all_occupancy(location)
        total = apartment_repo.get_total_apartments(location)
        vacant = total - occupied
        title_loc = _title_location(location)

        labels = [f"Occupied\\n{occupied} units", f"Vacant\\n{vacant} units"]
        values = [occupied, vacant]
        colors = [THEME.charts.accent_green, THEME.charts.accent_orange]

        return PieChart.create(
            parent=None,
            labels=labels,
            values=values,
            colors=colors,
            title=f"Occupancy Distribution - {title_loc}",
            explode=(0.05, 0),
            return_figure=True,
        )

    @staticmethod
    def create_revenue_bar_chart(location=None):
        apartment_repo = ApartmentsRepository()
        actual = apartment_repo.get_monthly_revenue(location)
        potential = apartment_repo.get_potential_revenue(location)
        lost = potential - actual
        title_loc = _title_location(location)

        categories = ["Actual Revenue", "Potential Revenue", "Lost Revenue"]
        values = [actual, potential, lost]
        colors = [THEME.charts.accent_green, THEME.charts.accent_blue, THEME.charts.accent_red]

        return ComparisonBarChart.create(
            parent=None,
            categories=categories,
            values=values,
            colors=colors,
            title=f"Revenue Comparison - {title_loc}",
            y_label="Revenue (GBP)",
            value_formatter="currency_decimal",
            return_figure=True,
        )


class LeaseGraphService:
    """Chart/report generation for lease visuals."""

    @staticmethod
    def create_lease_trend_graph(parent, location=None, start_date=None, end_date=None, grouping="month"):
        lease_repo = LeaseAgreementsRepository()
        data = lease_repo.get_lease_trend_timeseries(
            location=location,
            start_date=start_date,
            end_date=end_date,
            grouping=grouping,
        )
        series_data = data.get("series") or []
        periods = [row.get("period") for row in series_data]
        new_values = np.array([int(row.get("new_leases") or 0) for row in series_data], dtype=float)
        active_values = np.array([int(row.get("active_leases") or 0) for row in series_data], dtype=float)
        expired_values = np.array([int(row.get("expired_leases") or 0) for row in series_data], dtype=float)

        title_location = _title_location(location)
        return TrendChart.create(
            parent,
            periods=periods,
            series=[
                ("Active Leases", active_values, THEME.charts.accent_green),
                ("New Leases", new_values, "#4A90E2"),
            ],
            title=f"Lease Trends - {title_location}",
            y_label="Number of Leases",
            y_formatter="number",
            fill_primary=True,
            fill_secondary=False,
            primary_color=THEME.charts.accent_green,
            secondary_axis=("Expired", expired_values, THEME.charts.accent_orange),
            show_kpi=False,
            show_toolbar=True,
            y_lim_dynamic=True,
        )

    @staticmethod
    def create_lease_status_pie_chart(location=None):
        lease_repo = LeaseAgreementsRepository()
        stats = lease_repo.get_lease_statistics(location)
        active = stats.get("active_leases", 0)
        expired = stats.get("expired_leases", 0)
        title_loc = _title_location(location)

        labels = [f"Active\\n{active} leases", f"Expired\\n{expired} leases"]
        values = [active, expired]
        colors = [THEME.charts.accent_green, THEME.charts.accent_red]

        return PieChart.create(
            parent=None,
            labels=labels,
            values=values,
            colors=colors,
            title=f"Lease Status Distribution - {title_loc}",
            explode=(0.05, 0),
            return_figure=True,
        )

    @staticmethod
    def create_lease_comparison_bar_chart(location=None):
        lease_repo = LeaseAgreementsRepository()
        stats = lease_repo.get_lease_statistics(location)
        active = stats.get("active_leases", 0)
        expired = stats.get("expired_leases", 0)
        expiring = stats.get("expiring_soon", 0)
        title_loc = _title_location(location)

        categories = ["Active", "Expired", "Expiring Soon"]
        values = [active, expired, expiring]
        colors = [THEME.charts.accent_green, THEME.charts.accent_red, THEME.charts.accent_orange]

        return ComparisonBarChart.create(
            parent=None,
            categories=categories,
            values=values,
            colors=colors,
            title=f"Lease Status Comparison - {title_loc}",
            y_label="Number of Leases",
            value_formatter="integer",
            return_figure=True,
        )


class FinanceGraphService:
    """Chart/report generation for finance visuals."""

    @staticmethod
    def create_financial_summary_graph(parent, location=None):
        invoices_repo = InvoicesRepository()
        summary = invoices_repo.get_financial_summary(location)
        total_invoiced = float(summary.get("total_invoiced", 0) or 0)
        total_collected = float(summary.get("total_collected", 0) or 0)
        outstanding = float(summary.get("outstanding", 0) or 0)
        late_count = int(summary.get("late_invoice_count", 0) or 0)

        title_location = _title_location(location)
        return BarChart.create(
            parent,
            labels=["Invoiced", "Collected", "Outstanding"],
            values=[total_invoiced, total_collected, outstanding],
            colors=[THEME.charts.accent_blue, THEME.charts.accent_green, THEME.charts.accent_orange],
            title=f"Financial Summary - {title_location}",
            y_label="Amount (GBP)",
            value_formatter="currency_decimal",
            overlay_text=f"Late invoices: {late_count}",
            bar_label_fontsize=10,
        )

    @staticmethod
    def create_collected_trend_graph(parent, location=None, start_date=None, end_date=None, grouping="month"):
        invoices_repo = InvoicesRepository()
        data = invoices_repo.get_collected_amount_timeseries(
            location=location,
            start_date=start_date,
            end_date=end_date,
            grouping=grouping,
        )
        series_data = data.get("series") or []
        periods = [row.get("period") for row in series_data]
        invoiced_values = np.array([float(row.get("total_invoiced") or 0) for row in series_data], dtype=float)
        collected_values = np.array([float(row.get("total_collected") or 0) for row in series_data], dtype=float)
        late_values = np.array([float(row.get("late_count") or 0) for row in series_data], dtype=float)

        title_location = _title_location(location)
        return TrendChart.create(
            parent,
            periods=periods,
            series=[
                ("Invoiced", invoiced_values, THEME.charts.accent_green),
                ("Payments", collected_values, "#6B7080"),
            ],
            title=f"Finance Trends - {title_location}",
            y_label="Amount (GBP)",
            y_formatter="currency",
            fill_primary=True,
            fill_secondary=True,
            primary_color=THEME.charts.accent_green,
            secondary_axis=("Late Invoices", late_values, "#8E929C"),
            kpi_style="circle",
            show_toolbar=True,
            y_lim_dynamic=True,
        )

    @staticmethod
    def create_financial_status_pie_chart(location=None):
        invoices_repo = InvoicesRepository()
        summary = invoices_repo.get_financial_summary(location)
        collected = summary["total_collected"]
        outstanding = summary["outstanding"]
        title_loc = _title_location(location)

        labels = [f"Collected\\nGBP {collected:,.2f}", f"Outstanding\\nGBP {outstanding:,.2f}"]
        values = [collected, outstanding]
        colors = [THEME.charts.accent_green, THEME.charts.accent_orange]

        return PieChart.create(
            parent=None,
            labels=labels,
            values=values,
            colors=colors,
            title=f"Financial Status - {title_loc}",
            explode=(0.05, 0),
            return_figure=True,
        )

    @staticmethod
    def create_financial_comparison_bar_chart(location=None):
        invoices_repo = InvoicesRepository()
        summary = invoices_repo.get_financial_summary(location)
        invoiced = summary["total_invoiced"]
        collected = summary["total_collected"]
        outstanding = summary["outstanding"]
        title_loc = _title_location(location)

        categories = ["Total Invoiced", "Collected", "Outstanding"]
        values = [invoiced, collected, outstanding]
        colors = [THEME.charts.accent_blue, THEME.charts.accent_green, THEME.charts.accent_red]

        return ComparisonBarChart.create(
            parent=None,
            categories=categories,
            values=values,
            colors=colors,
            title=f"Financial Comparison - {title_loc}",
            y_label="Amount (GBP)",
            value_formatter="currency_decimal",
            return_figure=True,
        )
"""
Contributors: Aaron Antal-Bento (23013693)

Service-backed dashboard adapters used for cross-role manager dashboard views."""

from __future__ import annotations

from services.admin_service import AdminService
from services.finance_service import FinanceService
from services.front_desk_service import FrontDeskService
from services.maintenance_service import MaintenanceService


class DashboardAdapter:
    """Lightweight adapter exposing dashboard callback methods expected by cards."""

    def __init__(self, username: str, role: str, location: str | None = None):
        self.username = username
        self.role = role
        self.location = location


class AdministratorDashboardAdapter(DashboardAdapter):
    def __init__(self, username: str, location: str):
        super().__init__(username, role="Administrator", location=location)

    def view_apartment_occupancy(self):
        return AdminService.view_apartment_occupancy(self.location)

    def get_total_apartments(self, location: str | None = None):
        return AdminService.get_total_apartments(location or self.location)

    def get_monthly_revenue(self, location: str | None = None):
        return AdminService.get_monthly_revenue(location or self.location)

    def get_potential_revenue(self, location: str | None = None):
        return AdminService.get_potential_revenue(location or self.location)

    def get_lease_date_range(self, location: str | None = None, grouping: str = "month"):
        return AdminService.get_lease_date_range(location or self.location, grouping=grouping)

    def get_lease_statistics(self, location: str | None = None):
        return AdminService.get_lease_statistics(location or self.location)

    def get_all_leases(self, location: str | None = None):
        return AdminService.get_all_leases(location or self.location)

    def get_all_users(self, location: str | None = None):
        return AdminService.get_all_users(location or self.location)

    def get_all_apartments(self, location: str | None = None):
        return AdminService.get_all_apartments(location or self.location)

    def create_account(self, values):
        return AdminService.create_account(self.location, values)

    def edit_account(self, user_data, values):
        return AdminService.edit_account(self.location, user_data, values)

    def delete_account(self, user_data):
        return AdminService.delete_account(user_data)

    def add_apartment(self, apartment_data):
        return AdminService.add_apartment(self.location, apartment_data)

    def delete_apartment(self, apartment_data):
        return AdminService.delete_apartment(apartment_data)

    def edit_apartment(self, apartment_data, values):
        return AdminService.edit_apartment(self.location, apartment_data, values)


class FinanceDashboardAdapter(DashboardAdapter):
    def __init__(self, username: str, location: str):
        super().__init__(username, role="Finance Manager", location=location)

    def generate_financial_reports(self, location: str = "all"):
        return FinanceService.generate_financial_reports(location)

    def get_finance_date_range(self, location: str, grouping: str = "month"):
        return FinanceService.get_finance_date_range(location, grouping=grouping)

    def get_unpaid_invoices(self, location: str = "all"):
        return FinanceService.get_unpaid_invoices(location)

    def get_invoices(self, location: str = "all", paid: int | None = None):
        return FinanceService.get_invoices(location, paid=paid)

    def get_late_invoices(self, location: str = "all"):
        return FinanceService.get_late_invoices(location)

    def get_payments(self, location: str = "all"):
        return FinanceService.get_payments(location)

    def get_all_tenant_names(self):
        return FinanceService.get_all_tenant_names()

    def create_invoice(self, values):
        return FinanceService.create_invoice(values)

    def update_invoice_row(self, row_data, updated_data):
        return FinanceService.update_invoice_row(row_data, updated_data)

    def delete_invoice_row(self, row_data):
        return FinanceService.delete_invoice_row(row_data)

    def record_payment(self, values):
        return FinanceService.record_payment(values)


class FrontDeskDashboardAdapter(DashboardAdapter):
    def __init__(self, username: str, location: str):
        super().__init__(username, role="Front Desk Staff", location=location)

    def register_tenant(self, values):
        return FrontDeskService.register_tenant(values)

    def get_tenant_info(self, tenant_id=None):
        return FrontDeskService.get_tenant_info(self.location, tenant_id)

    def update_tenant(self, tenant_id, values):
        return FrontDeskService.update_tenant(tenant_id, values)

    def register_maintenance_request(self, values):
        return FrontDeskService.register_maintenance_request(values)

    def register_complaint(self, values):
        return FrontDeskService.register_complaint(values)

    def get_all_apartments(self, location: str = "all"):
        return FrontDeskService.get_all_apartments(location)

    def get_tenant_by_id(self, tenant_id: int):
        return FrontDeskService.get_tenant_by_id(self.location, tenant_id)

    def search_tenants(self, search_term: str):
        return FrontDeskService.search_tenants(self.location, search_term)

    def get_all_tenants(self):
        return FrontDeskService.get_all_tenants(self.location)

    def get_all_complaints(self):
        return FrontDeskService.get_all_complaints(self.location)

    def update_complaint_status(self, complaint_id: int, resolved: int):
        return FrontDeskService.update_complaint_status(complaint_id, resolved)

    def delete_complaint(self, complaint_id: int):
        return FrontDeskService.delete_complaint(complaint_id)

    def get_all_cities(self):
        return FrontDeskService.get_all_cities()

    def get_maintenance_requests(
        self,
        location: str | None = None,
        completed: int | None = None,
        priority: int | None = None,
        compact: bool = False,
    ):
        return FrontDeskService.get_maintenance_requests(
            location or self.location,
            completed=completed,
            priority=priority,
            compact=compact,
        )

    def update_maintenance_request(self, request_id: int, **kwargs):
        return FrontDeskService.update_maintenance_request(request_id, **kwargs)

    def delete_maintenance_request(self, request_id: int):
        return FrontDeskService.delete_maintenance_request(request_id)


class MaintenanceDashboardAdapter(DashboardAdapter):
    def __init__(self, username: str, location: str):
        super().__init__(username, role="Maintenance Staff", location=location)

    def get_maintenance_stats(self, location: str = "all"):
        return MaintenanceService.get_maintenance_stats(location)

    def create_maintenance_request(self, values):
        return MaintenanceService.create_maintenance_request(values)

    def update_maintenance_request_row(self, row_data, updated_data):
        return MaintenanceService.update_maintenance_request_row(row_data, updated_data)

    def delete_maintenance_request_row(self, row_data):
        return MaintenanceService.delete_maintenance_request_row(row_data)

    def complete_maintenance_request(self, values):
        return MaintenanceService.complete_maintenance_request(values)

    def schedule_maintenance(self, values):
        return MaintenanceService.schedule_maintenance(values)

    def get_all_cities(self):
        return MaintenanceService.get_all_cities()

    def get_maintenance_requests(
        self,
        location: str = "all",
        completed: int | None = None,
        priority: int | None = None,
        compact: bool = False,
    ):
        return MaintenanceService.get_maintenance_requests(
            location=location,
            completed=completed,
            priority=priority,
            compact=compact,
        )

    def update_maintenance_request(self, request_id: int, **kwargs):
        return MaintenanceService.update_maintenance_request(request_id, **kwargs)

    def delete_maintenance_request(self, request_id: int):
        return MaintenanceService.delete_maintenance_request(request_id)

    def get_apartments_with_tenants(self, location: str = "all"):
        return MaintenanceService.get_apartments_with_tenants(location)

    def get_scheduled_maintenance(self, location: str = "all"):
        return MaintenanceService.get_scheduled_maintenance(location)

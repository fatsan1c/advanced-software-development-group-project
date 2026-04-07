import customtkinter as ctk
from pages.components.dashboard_cards import (
    load_manager_account_card,
    load_manager_business_expansion_card,
    load_manager_dashboards_launcher_card,
    load_manager_occupancy_card,
    load_manager_report_card,
    render_dashboard_cards,
)
from models.user import User
from services.manager_service import ManagerService
from models.user_roles.dashboard_adapters import (
    AdministratorDashboardAdapter,
    FinanceDashboardAdapter,
    FrontDeskDashboardAdapter,
    MaintenanceDashboardAdapter,
)

class Manager(User):
    """Manager user with business-wide access and control."""

    CARD_SEQUENCE = [
        {"row": 1, "builder": load_manager_report_card},
        {"row": 2, "builder": load_manager_occupancy_card},
        {"row": 2, "builder": load_manager_account_card},
        {"row": 3, "builder": load_manager_business_expansion_card},
        {"row": 4, "builder": load_manager_dashboards_launcher_card},
    ]
    
    def __init__(self, username: str, location: str | None = None):
        super().__init__(username, role="Manager", location=location)

    def load_homepage_content(self, home_page):
        """Render manager dashboard cards in configured order."""
        super().load_homepage_content(home_page)
        render_dashboard_cards(home_page, self, self.CARD_SEQUENCE)

    def view_apartment_occupancy(self, location: str = "all"):
        """Return occupied apartment count for the selected location scope."""
        return ManagerService.view_apartment_occupancy(location)

    def get_total_apartments(self, location: str = "all"):
        """Return apartment unit count for the selected location scope."""
        return ManagerService.get_total_apartments(location)

    def get_monthly_revenue(self, location: str = "all"):
        """Return monthly revenue for the selected location scope."""
        return ManagerService.get_monthly_revenue(location)

    def get_potential_revenue(self, location: str = "all"):
        """Return potential revenue for the selected location scope."""
        return ManagerService.get_potential_revenue(location)

    def get_lease_date_range(self, location: str = "all", grouping: str = "month"):
        """Return lease graph date range for the selected location scope."""
        return ManagerService.get_lease_date_range(location, grouping=grouping)

    def get_all_users(self):
        """Return all users for manager account-management views."""
        return ManagerService.get_all_users()

    def get_all_cities(self):
        """Return all city names for manager dropdowns and filters."""
        return ManagerService.get_all_cities()

    def get_all_locations(self):
        """Return all location rows for manager location-management views."""
        return ManagerService.get_all_locations()

    def get_all_apartments(self, location: str = "all"):
        """Return apartments for a selected location scope."""
        return ManagerService.get_all_apartments(location)

    def create_account(self, values):
        """Create a user account."""
        return ManagerService.create_account(values)

    def edit_account(self, user_data, values):
        """Edit a user account."""
        return ManagerService.edit_account(user_data, values)

    def delete_account(self, user_data):
        """Delete a user account."""
        return ManagerService.delete_account(user_data)

    def expand_business(self, new_location):
        """Add a new business location."""
        return ManagerService.expand_business(new_location)

    def edit_location(self, location_data, values):
        """Edit a location."""
        return ManagerService.edit_location(location_data, values)

    def delete_location(self, location_data):
        """Delete a location."""
        return ManagerService.delete_location(location_data)

    def add_apartment(self, apartment_data):
        """Add an apartment."""
        return ManagerService.add_apartment(apartment_data)

    def delete_apartment(self, apartment_data):
        """Delete an apartment."""
        return ManagerService.delete_apartment(apartment_data)

    def edit_apartment(self, apartment_data, values):
        """Edit apartment details."""
        return ManagerService.edit_apartment(apartment_data, values)

    def _resolve_dashboard_location(self, selected_location: str | None) -> str:
        if selected_location and selected_location not in {"All Locations", "None"}:
            return selected_location

        if self.location:
            return self.location

        try:
            locations = ManagerService.get_all_cities()
            return locations[0] if locations else ""
        except Exception:
            return ""

    def _build_cross_role_dashboard(self, dashboard_key: str, location_context: str):
        if dashboard_key == "administrator":
            from models.user_roles.administrator import Administrator

            return AdministratorDashboardAdapter(self.username, location_context), Administrator.CARD_SEQUENCE

        if dashboard_key == "finance":
            from models.user_roles.finance_manager import FinanceManager

            return FinanceDashboardAdapter(self.username, location_context), FinanceManager.CARD_SEQUENCE

        if dashboard_key == "front_desk":
            from models.user_roles.front_desk_staff import FrontDeskStaff

            return FrontDeskDashboardAdapter(self.username, location_context), FrontDeskStaff.CARD_SEQUENCE

        if dashboard_key == "maintenance":
            from models.user_roles.maintenance_staff import MaintenanceStaff

            return MaintenanceDashboardAdapter(self.username, location_context), MaintenanceStaff.CARD_SEQUENCE

        return None, None

    def _open_cross_role_dashboard(self, dashboard_key: str, selected_location: str | None):
        """Open the selected role dashboard in a popup using service-backed adapters."""
        location_context = self._resolve_dashboard_location(selected_location)
        dashboard_user, card_sequence = self._build_cross_role_dashboard(dashboard_key, location_context)
        if dashboard_user is None:
            return "Unable to load dashboard."

        popup = ctk.CTkToplevel()
        popup.title(f"{dashboard_user.role} Dashboard")
        popup.geometry("1220x780")
        popup.minsize(1024, 680)

        class _RoleDashboardContainer(ctk.CTkFrame):
            def __init__(self, parent):
                super().__init__(parent, fg_color="transparent")
                self._window = parent

            def close_page(self):
                self._window.destroy()

        container = _RoleDashboardContainer(popup)
        container.pack(fill="both", expand=True)
        render_dashboard_cards(container, dashboard_user, card_sequence)

        popup.lift()
        popup.focus_force()
        return True

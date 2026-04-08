import pages.components.page_elements as pe
from pages.components.dashboard_cards import (
    load_manager_account_card,
    load_manager_business_expansion_card,
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
    ]

    DASHBOARD_TABS = [
        ("Manager", "manager"),
        ("Administrator", "administrator"),
        ("Finance", "finance"),
        ("Front Desk", "front_desk"),
        ("Maintenance", "maintenance"),
    ]
    
    def __init__(self, username: str, location: str | None = None):
        super().__init__(username, role="Manager", location=location)

    def load_homepage_content(self, home_page):
        """Render manager dashboard with top tab selector and cards."""
        super().load_homepage_content(home_page)

        state = {"container": None}

        def show_dashboard(tab_key: str, selected_location: str):
            if state["container"] is not None:
                state["container"].pack_forget()
                state["container"].destroy()

            if tab_key == "manager":
                dashboard_user, card_sequence = self, self.CARD_SEQUENCE
            else:
                location_context = self._resolve_dashboard_location(selected_location)
                print(tab_key == "administrator", location_context == None)
                if tab_key == "administrator" and location_context == None: location_context = "Bristol"
                dashboard_user, card_sequence = self._build_cross_role_dashboard(tab_key, location_context)

            if dashboard_user is None or card_sequence is None:
                return "Unable to load dashboard."

            state["container"] = render_dashboard_cards(home_page, dashboard_user, card_sequence)
            return True

        dashboard_tabs = pe.DashboardTabsMenu(
            home_page,
            tabs=self.DASHBOARD_TABS,
            on_tab_selected=show_dashboard,
            on_location_changed=show_dashboard,
            title="All Dashboards",
            get_locations=self.get_all_cities,
            initial_location=self.location or "All Locations",
            default_tab_key="manager",
        )
        dashboard_tabs.select_tab("manager", invoke_callback=True)

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
        if selected_location in {"All Locations", "all", "None"}:
            return None
        
        return selected_location

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

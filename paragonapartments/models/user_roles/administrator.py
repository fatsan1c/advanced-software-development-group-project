"""Contributors: Aaron Antal-Bento (23013693)"""

from pages.components.dashboard_cards import (
    load_admin_account_card,
    load_admin_apartment_card,
    load_admin_lease_card,
    load_admin_occupancy_card,
    load_admin_report_card,
    render_dashboard_with_location_selector,
)
from models.user import User
from services.admin_service import AdminService


class Administrator(User):
    """Administrator with location-specific management capabilities."""

    CARD_SEQUENCE = [
        {"row": 1, "builder": load_admin_occupancy_card},
        {"row": 1, "builder": load_admin_account_card},
        {"row": 2, "builder": load_admin_lease_card},
        {"row": 2, "builder": load_admin_report_card},
        {"row": 3, "builder": load_admin_apartment_card},
    ]
    
    def __init__(self, username: str, location: str = ""):
        super().__init__(username, role="Administrator", location=location)
    
    def load_homepage_content(self, home_page):
        """Render administrator dashboard cards in configured order."""
        super().load_homepage_content(home_page)
        render_dashboard_with_location_selector(
            home_page,
            self,
            self.CARD_SEQUENCE,
            get_locations=AdminService.get_all_cities,
        )

    def view_apartment_occupancy(self):
        """Return occupied apartment count for this administrator location."""
        return AdminService.view_apartment_occupancy(self.location)

    def get_total_apartments(self, location: str | None = None):
        """Return apartment unit count for this administrator location."""
        return AdminService.get_total_apartments(location or self.location)

    def get_monthly_revenue(self, location: str | None = None):
        """Return monthly revenue for this administrator location."""
        return AdminService.get_monthly_revenue(location or self.location)

    def get_potential_revenue(self, location: str | None = None):
        """Return potential revenue for this administrator location."""
        return AdminService.get_potential_revenue(location or self.location)

    def get_lease_date_range(self, location: str | None = None, grouping: str = "month"):
        """Return lease graph date range for this administrator location."""
        return AdminService.get_lease_date_range(location or self.location, grouping=grouping)

    def get_lease_statistics(self, location: str | None = None):
        """Return lease statistics for this administrator location."""
        return AdminService.get_lease_statistics(location or self.location)

    def get_all_leases(self, location: str | None = None):
        """Return all leases for this administrator location."""
        return AdminService.get_all_leases(location or self.location)

    def get_all_users(self, location: str | None = None):
        """Return users scoped to this administrator location."""
        return AdminService.get_all_users(location or self.location)

    def get_all_apartments(self, location: str | None = None):
        """Return apartments scoped to this administrator location."""
        return AdminService.get_all_apartments(location or self.location)

    def create_account(self, values):
        """Create a user account scoped to this administrator location."""
        return AdminService.create_account(self.location, values)

    def edit_account(self, user_data, values):
        """Edit a user account scoped to this administrator location."""
        return AdminService.edit_account(self.location, user_data, values)

    def delete_account(self, user_data):
        """Delete a user account."""
        return AdminService.delete_account(user_data)

    def add_apartment(self, apartment_data):
        """Add an apartment in this administrator location."""
        return AdminService.add_apartment(self.location, apartment_data)

    def delete_apartment(self, apartment_data):
        """Delete an apartment."""
        return AdminService.delete_apartment(apartment_data)

    def edit_apartment(self, apartment_data, values):
        """Edit an apartment in this administrator location."""
        return AdminService.edit_apartment(self.location, apartment_data, values)
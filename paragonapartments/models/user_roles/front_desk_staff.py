"""Contributors: Oliver Mercer (24026901), Nickolas Greiner (24018357)"""

from models.user import User
from pages.components.dashboard_cards import (
    load_front_desk_apartment_search_card,
    load_front_desk_complaints_card,
    load_front_desk_maintenance_card,
    load_front_desk_tenant_card,
    render_dashboard_cards,
)
from services.front_desk_service import FrontDeskService


class FrontDeskStaff(User):
    """Front desk staff with tenant management and maintenance request handling."""

    CARD_SEQUENCE = [
        {"row": 1, "builder": load_front_desk_tenant_card},
        {"row": 2, "builder": load_front_desk_apartment_search_card},
        {"row": 3, "builder": load_front_desk_maintenance_card},
        {"row": 3, "builder": load_front_desk_complaints_card},
    ]

    def __init__(self, username: str, location: str = ""):
        super().__init__(username, role="Front Desk Staff", location=location)

    def load_homepage_content(self, home_page):
        """Render front desk dashboard cards in configured order."""
        super().load_homepage_content(home_page)
        render_dashboard_cards(home_page, self, self.CARD_SEQUENCE)

    def register_tenant(self, values):
        """Register a tenant and create associated lease/occupancy records."""
        return FrontDeskService.register_tenant(values)

    def get_tenant_info(self, tenant_id=None):
        """Return formatted tenant details for this role location."""
        return FrontDeskService.get_tenant_info(self.location, tenant_id)

    def update_tenant(self, tenant_id, values):
        """Update tenant details."""
        return FrontDeskService.update_tenant(tenant_id, values)

    def register_maintenance_request(self, values):
        """Register a maintenance request."""
        return FrontDeskService.register_maintenance_request(values)

    def register_complaint(self, values):
        """Register a tenant complaint."""
        return FrontDeskService.register_complaint(values)

    def get_all_apartments(self, location: str = "all"):
        """Return apartments for a location scope."""
        return FrontDeskService.get_all_apartments(location)

    def get_tenant_by_id(self, tenant_id: int):
        """Return a tenant by ID scoped to this role location."""
        return FrontDeskService.get_tenant_by_id(self.location, tenant_id)

    def search_tenants(self, search_term: str):
        """Search tenants scoped to this role location."""
        return FrontDeskService.search_tenants(self.location, search_term)

    def get_all_tenants(self):
        """Return all tenants scoped to this role location."""
        return FrontDeskService.get_all_tenants(self.location)

    def get_all_complaints(self):
        """Return all complaints scoped to this role location."""
        return FrontDeskService.get_all_complaints(self.location)

    def update_complaint_status(self, complaint_id: int, resolved: int):
        """Update complaint status."""
        return FrontDeskService.update_complaint_status(complaint_id, resolved)

    def delete_complaint(self, complaint_id: int):
        """Delete complaint by ID."""
        return FrontDeskService.delete_complaint(complaint_id)

    def get_all_cities(self):
        """Return all city names."""
        return FrontDeskService.get_all_cities()

    def get_maintenance_requests(
        self,
        location: str | None = None,
        completed: int | None = None,
        priority: int | None = None,
        compact: bool = False,
    ):
        """Return maintenance requests for location with optional filters."""
        return FrontDeskService.get_maintenance_requests(
            location or self.location,
            completed=completed,
            priority=priority,
            compact=compact,
        )

    def update_maintenance_request(self, request_id: int, **kwargs):
        """Update maintenance request fields by ID."""
        return FrontDeskService.update_maintenance_request(request_id, **kwargs)

    def delete_maintenance_request(self, request_id: int):
        """Delete maintenance request by ID."""
        return FrontDeskService.delete_maintenance_request(request_id)

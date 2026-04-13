"""Contributors: Ollie Churchley (23020494)"""

from pages.components.dashboard_cards import (
    load_maintenance_complete_request_card,
    load_maintenance_create_request_card,
    load_maintenance_pending_requests_card,
    load_maintenance_schedule_request_card,
    load_maintenance_summary_card,
    render_dashboard_cards,
)
from models.user import User
from services.maintenance_service import MaintenanceService


class MaintenanceStaff(User):
    """Maintenance staff with ability to view, manage, and resolve maintenance requests."""

    CARD_SEQUENCE = [
        {"row": 1, "builder": load_maintenance_summary_card},
        {"row": 1, "builder": load_maintenance_pending_requests_card},
        {"row": 2, "builder": load_maintenance_complete_request_card},
        {"row": 2, "builder": load_maintenance_schedule_request_card},
        {"row": 3, "builder": load_maintenance_create_request_card},
    ]
    
    def __init__(self, username: str, location: str | None = None):
        super().__init__(username, role="Maintenance Staff", location=location)

    def load_homepage_content(self, home_page):
        """Render maintenance dashboard cards in configured order."""
        super().load_homepage_content(home_page)
        render_dashboard_cards(home_page, self, self.CARD_SEQUENCE)

    def get_maintenance_stats(self, location: str = "all"):
        """Return maintenance summary metrics for the selected location."""
        return MaintenanceService.get_maintenance_stats(location)

    def create_maintenance_request(self, values):
        """Create a maintenance request."""
        return MaintenanceService.create_maintenance_request(values)

    def update_maintenance_request_row(self, row_data, updated_data):
        """Update an existing maintenance request row."""
        return MaintenanceService.update_maintenance_request_row(row_data, updated_data)

    def delete_maintenance_request_row(self, row_data):
        """Delete a maintenance request row."""
        return MaintenanceService.delete_maintenance_request_row(row_data)

    def complete_maintenance_request(self, values):
        """Mark a maintenance request as complete."""
        return MaintenanceService.complete_maintenance_request(values)

    def schedule_maintenance(self, values):
        """Schedule a maintenance request."""
        return MaintenanceService.schedule_maintenance(values)

    def get_all_cities(self):
        """Return all city names for maintenance filters."""
        return MaintenanceService.get_all_cities()

    def get_maintenance_requests(
        self,
        location: str = "all",
        completed: int | None = None,
        priority: int | None = None,
        compact: bool = False,
    ):
        """Return maintenance requests for location with optional filters."""
        return MaintenanceService.get_maintenance_requests(
            location=location,
            completed=completed,
            priority=priority,
            compact=compact,
        )

    def update_maintenance_request(self, request_id: int, **kwargs):
        """Update maintenance request fields by ID."""
        return MaintenanceService.update_maintenance_request(request_id, **kwargs)

    def delete_maintenance_request(self, request_id: int):
        """Delete maintenance request by ID."""
        return MaintenanceService.delete_maintenance_request(request_id)

    def get_apartments_with_tenants(self, location: str = "all"):
        """Return apartments with active tenants for request creation."""
        return MaintenanceService.get_apartments_with_tenants(location)

    def get_scheduled_maintenance(self, location: str = "all"):
        """Return scheduled maintenance items for location."""
        return MaintenanceService.get_scheduled_maintenance(location)
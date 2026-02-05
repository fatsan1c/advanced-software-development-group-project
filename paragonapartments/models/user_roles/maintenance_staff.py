import pages.components.page_elements as pe
from models.user import User


class MaintenanceStaff(User):
    """Maintenance staff with ability to view and update maintenance requests."""
    
    def __init__(self, username: str, location: str = ""):
        super().__init__(username, role="Maintenance Staff", location=location)

    def view_maintenance_requests(self):
        """View all maintenance requests for this location."""
        print("Viewing maintenance requests...")

    def update_request_status(self, request_id: int, status: str):
        """Update the status of a maintenance request."""
        print(f"Updating request {request_id} to status '{status}' located at {self.location}")
    
    def load_homepage_content(self, home_page):
        """Load Maintenance Staff-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)
        
        row1 = pe.row_container(parent=home_page)
        
        requests_card = pe.function_card(row1, "Maintenance Requests", side="left")
        
        pe.action_button(
            requests_card,
            text="View Requests",
            command=lambda: self.view_maintenance_requests()
        )
        
        status_card = pe.function_card(row1, "Update Status", side="left")
        
        pe.action_button(
            status_card,
            text="Update Request",
            command=lambda: self.update_request_status(1, "In Progress")
        )
        
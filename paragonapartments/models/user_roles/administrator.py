import pages.components.page_elements as pe
from models.user import User


class Administrator(User):
    """Administrator with location-specific management capabilities."""
    
    def __init__(self, username: str, location: str = ""):
        super().__init__(username, role="Administrator", location=location)

    def create_account(self, username: str, role: str):
        """Create a new user account at this administrator's location."""
        print(f"Creating account for {username} with role {role} at location {self.location}")

    def edit_account(self, username: str, role: str):
        """Edit an existing user account at this administrator's location."""
        print(f"Editing account for {username} to role {role} at location {self.location}")

    def manage_apartments(self, action: str):
        """Perform management actions on apartments at this location."""
        print(f"Performing '{action}' on apartments at location: {self.location}")

    def generate_reports(self):
        """Generate reports for this location."""
        print("Generating reports for this location...")

    def track_lease_agreement(self, lease_id: int):
        """Track lease agreements for this location."""
        print("Tracking lease agreements...")
    
    def load_homepage_content(self, home_page):
        """Load Administrator-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)
        
        row1 = pe.row_container(parent=home_page)
        
        accounts_card = pe.function_card(row1, "Manage Accounts", side="left")
        
        pe.action_button(
            accounts_card,
            text="Create Account",
            command=lambda: self.create_account("newuser", "admin")
        )

        pe.action_button(
            accounts_card,
            text="Edit Account",
            command=lambda: self.edit_account("existinguser", "manager")
        )

        appartments_card = pe.function_card(row1, "Manage Apartments", side="left")

        pe.action_button(
            appartments_card,
            text="View Apartments",
            command=lambda: self.manage_apartments("view")
        )

        row2 = pe.row_container(parent=home_page)

        reports_card = pe.function_card(row2, "Generate Reports", side="left")

        pe.action_button(
            reports_card,
            text="Generate",
            command=lambda: self.generate_reports()
        )

        lease_card = pe.function_card(row2, "Track Lease Agreement", side="left")

        pe.action_button(
            lease_card,
            text="Track Lease",
            command=lambda: self.track_lease_agreement(1)
        )
        
import pages.components.page_elements as pe
from models.user import User


class Administrator(User):
    """Administrator with location-specific management capabilities."""
    
    def __init__(self, username: str, location: str = ""):
        super().__init__(username, role="Administrator", location=location)

# ============================= v Admin functions v  =====================================
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
# ============================= ^ Admin functions ^ =====================================
    
# ============================= v Homepage UI Content v =====================================
    def load_homepage_content(self, home_page, home_page_instance=None):
        """Load Administrator-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page, home_page_instance)
        
        # Create a row container for the administrator's homepage content
        row1 = pe.row_container(parent=home_page)
        
        # Add function card for account management
        self.load_account_content(row1)

        # Add function card for apartment management
        self.load_apartment_content(row1)

        row2 = pe.row_container(parent=home_page)

        # Add function card for reports and lease tracking
        self.load_reports_content(row2)

        self.load_lease_content(row2)
        
    def load_account_content(self, row):
        accounts_card = pe.function_card(row, "Manage Accounts", side="left")
        
        # Create account button for administrators location
        pe.action_button(
            accounts_card,
            text="Create Account",
            command=lambda: self.create_account("newuser", "admin")
        )

        # Edit account button for administrators location
        pe.action_button(
            accounts_card,
            text="Edit Account",
            command=lambda: self.edit_account("existinguser", "manager")
        )

    def load_apartment_content(self, row):
        appartments_card = pe.function_card(row, "Manage Apartments", side="left")

        # View apartments button for administrators location
        pe.action_button(
            appartments_card,
            text="View Apartments",
            command=lambda: self.manage_apartments("view")
        )

    def load_reports_content(self, row):
        reports_card = pe.function_card(row, "Generate Reports", side="left")

        # Generate reports button for administrators location
        pe.action_button(
            reports_card,
            text="Generate",
            command=lambda: self.generate_reports()
        )

    def load_lease_content(self, row):
        lease_card = pe.function_card(row, "Track Lease Agreement", side="left")

        # Track lease agreement button for administrators location
        pe.action_button(
            lease_card,
            text="Track Lease",
            command=lambda: self.track_lease_agreement(1)
        )
# ============================= ^ Homepage UI Content ^ =====================================
import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.user_repository as user_repo
import database_operations.repos.location_repository as location_repo

def create_user(username: str, user_type: str, location: str = ""):
    """Factory function to create the appropriate user class based on user type"""
    user_type_lower = user_type.lower().replace(" ", "")
    
    if user_type_lower == "administrator" or user_type_lower == "admin":
        return Administrator(username, location)
    elif user_type_lower == "manager":
        return Manager(username)
    elif user_type_lower == "financemanager" or user_type_lower == "finance":
        return FinanceManager(username)
    elif user_type_lower == "frontdeskstaff" or user_type_lower == "frontdesk":
        return FrontDeskStaff(username, location)
    elif user_type_lower == "maintenancestaff" or user_type_lower == "maintenance":
        return MaintenanceStaff(username, location)
    else:
        return User(username, user_type, location)


class User:
    """Base user class for all user types in the system."""
    
    def __init__(self, username: str, role: str, location: str = ""):
        self.username = username
        self.role = role
        self.location = location
    
    def view_profile(self):
        """Return a string representation of the user profile."""
        return f"User(username='{self.username}', role='{self.role}', location='{self.location}')"
    
    def logout(self, home_page):
        """Log the user out of the system."""
        print(f"{self.username} has logged out.")
        home_page.close_page()

    def load_homepage_content(self, home_page):
        """Initialize and display home page content."""
        # Centered content wrapper
        top_content = pe.content_container(parent=home_page, anchor="nw", fill="x")

        ctk.CTkLabel(
            top_content, 
            text="Paragon Apartments", 
            font=("Arial", 24)
        ).pack(side="left", padx=15)

        ctk.CTkLabel(
            top_content, 
            text=self.role + " Dashboard" + (f" - {self.location}" if self.location else ""),
            font=("Arial", 24)
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(
            top_content, 
            text="Logout",
            width=80,
            height=40,
            font=("Arial", 17),
            command=lambda: self.logout(home_page)
        ).pack(side="right", padx=10)


class Manager(User):
    """Manager user with business-wide access and control."""
    
    def __init__(self, username: str):
        super().__init__(username, role="Manager")

    def view_apartment_occupancy(self, location: str):
        """View apartment occupancy for a specific location."""
        print(f"Viewing apartment occupancy for location: {location}")

    def generate_reports(self, location: str):
        """Generate maintenance reports for a location."""
        print("Generating maintenance report...")

    def create_account(self, values):
        """Create a new user account with specified role and location."""
        username = values.get('Username', '')
        role = values.get('Role', '')
        password = values.get('Password', '')
        location = values.get('Location', None)
        
        # Handle "None" string from dropdown
        if location and location != "None":
            location_id = location_repo.get_location_id_by_city(location)
        else:
            location_id = None

        try:
            #Database operation
            user_repo.create_user(username, password, role, location_id)
            return True  # Success
        except Exception as e:
            return f"Failed to create account: {str(e)}"

    def delete_account(self, values):
        """Delete an existing user account by username or ID."""
        user_identifier = values.get('Users', None)
        user_id = values.get('ID', None)

        try:
            if user_identifier and user_identifier != "None":
                # Assuming username is unique
                user = user_repo.get_user_by_username(user_identifier)
                if user:
                    user_repo.delete_user(user['user_ID'])
                else:
                    return "User not found."
            elif user_id:
                user_repo.delete_user(int(user_id))
            else:
                return "No valid user identifier provided."

            return True  # Success
        except Exception as e:
            return f"Failed to delete account: {str(e)}"

    def expand_business(self, new_location: str):
        """Expand business to a new location."""
        print(f"Expanding business to new location: {new_location}")
    
    def load_homepage_content(self, home_page):
        """Load Manager-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)

        container = pe.scrollable_container(parent=home_page)

        # First row - 2 cards
        row1 = pe.row_container(parent=container)
        
        self.load_occupancy_content(row1)

        self.load_account_content(row1)

        # Second row - full width card
        row2 = pe.row_container(parent=container)

        self.load_report_content(row2)

        # Third row - full width card
        row3 = pe.row_container(parent=container)
        
        self.load_business_expansion_content(row3)

    def load_occupancy_content(self, row):
        occupancy_card = pe.function_card(row, "Apartment Occupancy", side="left")
        
        pe.action_button(
            occupancy_card,
            text="View All Locations",
            command=lambda: self.view_apartment_occupancy("all")
        )

        pe.action_button(
            occupancy_card,
            text="View Bristol",
            command=lambda: self.view_apartment_occupancy("bristol")
        )

    def load_account_content(self, row):
        accounts_card = pe.function_card(row, "Manage Accounts", side="left")

        fields = [
            {'name': 'Username', 'type': 'text', 'required': True},
            {'name': 'Role', 'type': 'dropdown', 'options': ['Admin', 'Manager', 'Finance Manager', 'Frontdesk', 'Maintenance'], 'required': True},
            {'name': 'Password', 'type': 'text', 'required': True},
            {'name': 'Location', 'type': 'dropdown', 'options': ['None'] + location_repo.get_all_cities(), 'required': False}
        ]

        pe.form_element(accounts_card, fields, name="Create", submit_text="Create Account", on_submit=self.create_account, small=True)

        def update_user_names(selected_value):
            """Refresh user list when dropdown is clicked."""
            return ['None'] + user_repo.get_all_usernames()

        fields = [
            {'name': 'Users', 'type': 'dropdown', 'options': ['None'] + user_repo.get_all_usernames(), 'dropdown_update': update_user_names},
            {'name': 'ID', 'type': 'text', 'small': True}
        ]

        pe.form_element(accounts_card, fields, name="Delete", submit_text="Delete Account", on_submit=self.delete_account, small=True)

    def load_report_content(self, row):
        reports_card = pe.function_card(row, "Generate Reports", side="left")

        pe.action_button(
            reports_card,
            text="Generate",
            command=lambda: self.generate_reports("bristol")
        )

    def load_business_expansion_content(self, row):
        expand_card = pe.function_card(row, "Expand Business", side="top")

        pe.action_button(
            expand_card,
            text="Add Location",
            command=lambda: self.expand_business("newlocation")
        )


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


class FinanceManager(User):
    """Finance manager with financial reporting and payment processing capabilities."""
    
    def __init__(self, username: str):
        super().__init__(username, role="Finance Manager")

    def generate_financial_reports(self):
        """Generate financial reports across all locations."""
        print("Generating financial reports...")

    def manage_invoices(self):
        """Manage invoices across all locations."""
        print("Managing invoices...")

    def view_late_payments(self):
        """View all late payments across the system."""
        print("Viewing late payments...")

    def process_payments(self, payment_id: int):
        """Process a payment with the given payment ID."""
        print(f"Processing payment with ID: {payment_id}")
    
    def load_homepage_content(self, home_page):
        """Load Finance Manager-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)

        row1 = pe.row_container(parent=home_page)
        
        reports_card = pe.function_card(row1, "Financial Reports", side="left")
        
        pe.action_button(
            reports_card,
            text="Generate Reports",
            command=lambda: self.generate_financial_reports()
        )

        invoices_card = pe.function_card(row1, "Manage Invoices", side="left")

        pe.action_button(
            invoices_card,
            text="View Invoices",
            command=lambda: self.manage_invoices()
        )

        row2 = pe.row_container(parent=home_page)

        payments_card = pe.function_card(row2, "Late Payments", side="left")

        pe.action_button(
            payments_card,
            text="View Late Payments",
            command=lambda: self.view_late_payments()
        )

        process_card = pe.function_card(row2, "Process Payments", side="left")

        pe.action_button(
            process_card,
            text="Process Payment",
            command=lambda: self.process_payments(1)
        )


class FrontDeskStaff(User):
    """Front desk staff with tenant management and maintenance request handling."""
    
    def __init__(self, username: str, location: str = ""):
        super().__init__(username, role="Front Desk Staff", location=location)

    def register_tenant(self, tenant_name: str, location: str, ni_number: str, name: str, 
                       phone_number: str, email: str, occupation: str, references: list, 
                       apartment_requirements: str, lease_period: str):
        """Register a new tenant with their details."""
        print(f"Registering tenant: {tenant_name} at location {location}")

    def get_tenant_info(self, tenant_id: int):
        """Retrieve information for a specific tenant."""
        print(f"Getting info for tenant ID: {tenant_id}")

    def register_maintenance_request(self, tenant_id: int, request_details: str):
        """Register a maintenance request for a tenant."""
        print(f"Registering maintenance request for tenant ID: {tenant_id} with details: {request_details}")

    def register_complaint(self, tenant_id: int, complaint_details: str):
        """Register a complaint from a tenant."""
        print(f"Registering complaint for tenant ID: {tenant_id} with details: {complaint_details}")

    def track_maintenance_request(self, request_id: int):
        """Track the status of a maintenance request."""
        print(f"Tracking maintenance request ID: {request_id}")
    
    def load_homepage_content(self, home_page):
        """Load Front Desk Staff-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)
        
        row1 = pe.row_container(parent=home_page)
        
        tenant_card = pe.function_card(row1, "Tenant Management", side="left")
        
        pe.action_button(
            tenant_card,
            text="Register Tenant",
            command=lambda: self.register_tenant("John Doe", self.location, "AB123456C", 
                                                 "John Doe", "555-1234", "john@example.com", 
                                                 "Engineer", [], "2 bedroom", "12 months")
        )
        
        pe.action_button(
            tenant_card,
            text="Get Tenant Info",
            command=lambda: self.get_tenant_info(1)
        )
        
        maintenance_card = pe.function_card(row1, "Maintenance Requests", side="left")
        
        pe.action_button(
            maintenance_card,
            text="Register Request",
            command=lambda: self.register_maintenance_request(1, "Broken faucet")
        )
        
        pe.action_button(
            maintenance_card,
            text="Track Request",
            command=lambda: self.track_maintenance_request(1)
        )
        
        complaints_card = pe.function_card(row1, "Complaints", side="left")
        
        pe.action_button(
            complaints_card,
            text="Register Complaint",
            command=lambda: self.register_complaint(1, "Noise complaint")
        )


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
def create_user(username: str, password: str, user_type: str, location: str = ""):
    """Factory function to create the appropriate user class based on user type"""
    user_type_lower = user_type.lower().replace(" ", "")
    
    if user_type_lower == "administrator" or user_type_lower == "admin":
        return Administrator(username, password, location)
    elif user_type_lower == "manager":
        return Manager(username, password)
    elif user_type_lower == "financemanager" or user_type_lower == "finance":
        return FinanceManager(username, password)
    elif user_type_lower == "frontdeskstaff" or user_type_lower == "frontdesk":
        return FrontDeskStaff(username, password, location)
    elif user_type_lower == "maintenancestaff" or user_type_lower == "maintenance":
        return MaintenanceStaff(username, password, location)
    else:
        return User(username, password, user_type, location)


class User:
    """Base user class for all user types in the system."""
    
    def __init__(self, username: str, password: str, role: str, location: str = ""):
        self.username = username
        self.password = password
        self.role = role
        self.location = location
    
    def view_profile(self):
        """Return a string representation of the user profile."""
        return f"User(username='{self.username}', role='{self.role}', location='{self.location}')"
    
    def logout(self):
        """Log the user out of the system."""
        print(f"{self.username} has logged out.")

class Manager(User):
    """Manager user with business-wide access and control."""
    
    def __init__(self, username: str, password: str):
        super().__init__(username, password, role="Manager")

    def view_apartment_occupancy(self, location: str):
        """View apartment occupancy for a specific location."""
        print(f"Viewing apartment occupancy for location: {location}")

    def generate_reports(self, location: str):
        """Generate maintenance reports for a location."""
        print("Generating maintenance report...")

    def create_account(self, username: str, password: str, role: str, location: str = ""):
        """Create a new user account with specified role and location."""
        print(f"Creating account for {username} with role {role} at location {location}")

    def expand_business(self, new_location: str):
        """Expand business to a new location."""
        print(f"Expanding business to new location: {new_location}")


class Administrator(User):
    """Administrator with location-specific management capabilities."""
    
    def __init__(self, username: str, password: str, location: str = ""):
        super().__init__(username, password, role="Administrator", location=location)

    def create_account(self, username: str, password: str, role: str):
        """Create a new user account at this administrator's location."""
        print(f"Creating account for {username} with role {role} at location {self.location}")

    def manage_apartments(self, action: str):
        """Perform management actions on apartments at this location."""
        print(f"Performing '{action}' on apartments at location: {self.location}")

    def generate_reports(self):
        """Generate maintenance reports for this location."""
        print("Generating maintenance report...")

    def track_lease_agreement(self, lease_id: int):
        """Track lease agreements for this location."""
        print("Tracking lease agreements...")


class FinanceManager(User):
    """Finance manager with financial reporting and payment processing capabilities."""
    
    def __init__(self, username: str, password: str):
        super().__init__(username, password, role="Finance Manager")

    def generate_financial_reports(self):
        """Generate financial reports across all locations."""
        print("Generating financial reports...")

    def view_late_payments(self):
        """View all late payments across the system."""
        print("Viewing late payments...")

    def process_payments(self, payment_id: int):
        """Process a payment with the given payment ID."""
        print(f"Processing payment with ID: {payment_id}")


class FrontDeskStaff(User):
    """Front desk staff with tenant management and maintenance request handling."""
    
    def __init__(self, username: str, password: str, location: str = ""):
        super().__init__(username, password, role="Front Desk Staff", location=location)

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


class MaintenanceStaff(User):
    """Maintenance staff with ability to view and update maintenance requests."""
    
    def __init__(self, username: str, password: str, location: str = ""):
        super().__init__(username, password, role="Maintenance Staff", location=location)

    def view_maintenance_requests(self):
        """View all maintenance requests for this location."""
        print("Viewing maintenance requests...")

    def update_request_status(self, request_id: int, status: str):
        """Update the status of a maintenance request."""
        print(f"Updating request {request_id} to status '{status}' located at {self.location}")
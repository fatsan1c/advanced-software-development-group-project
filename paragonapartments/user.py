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
    def __init__(self, username: str, password: str, role: str, location: str = ""):
        self.username = username
        self.password = password
        self.role = role
        self.location = location
    
    def veiwProfile(self):
        return f"User(username='{self.username}', role='{self.role}', location='{self.location}')"
    
    def logout(self):
        print(f"{self.username} has logged out.")

class Manager(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password, role="Manager")

    def veiwAppartmentOccupancy(self, location: str):
        print(f"Viewing apartment occupancy for location: {location}")

    def generateReports(self, location: str):
        print("Generating maintenance report...")

    def createAccount(self, username: str, password: str, role: str, location: str = ""):
        print(f"Creating account for {username} with role {role} at location {location}")

    def expandBusiness(self, new_location: str):
        print(f"Expanding business to new location: {new_location}")


class Administrator(User):
    def __init__(self, username: str, password: str, location: str = ""):
        super().__init__(username, password, role="Administrator", location=location)

    def createAccount(self, username: str, password: str, role: str):
        print(f"Creating account for {username} with role {role} at location {self.location}")

    def manageApartments(self, action: str):
        print(f"Performing '{action}' on apartments at location: {self.location}")

    def generateReports(self):
        print("Generating maintenance report...")

    def trackLeaseAgreement(self, lease_id: int):
        print("Tracking lease agreements...")


class FinanceManager(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password, role="Finance Manager")

    def generateFinancialReports(self):
        print("Generating financial reports...")

    def viewLatePayments(self):
        print("Viewing late payments...")

    def processPayments(self, payment_id: int):
        print(f"Processing payment with ID: {payment_id}")


class FrontDeskStaff(User):
    def __init__(self, username: str, password: str, location: str = ""):
        super().__init__(username, password, role="Front Desk Staff", location=location)

    def registerTenant(self, tenant_name: str, location, NInumber, name, phone_number, email, occupation, references, apartment_requirements, lease_period):
        print(f"Registering tenant: {tenant_name} at location {location}")

    def getTenantInfo(self, tenant_id: int):
        print(f"Getting info for tenant ID: {tenant_id}")

    def registerMaintenanceRequest(self, tenant_id: int, request_details: str):
        print(f"Registering maintenance request for tenant ID: {tenant_id} with details: {request_details}")

    def registerComplaint(self, tenant_id: int, complaint_details: str):
        print(f"Registering complaint for tenant ID: {tenant_id} with details: {complaint_details}")

    def trackMaintenanceRequest(self, request_id: int):
        print(f"Tracking maintenance request ID: {request_id}")


class MaintenanceStaff(User):
    def __init__(self, username: str, password: str, location: str = ""):
        super().__init__(username, password, role="Maintenance Staff", location=location)

    def viewMaintenanceRequests(self):
        print("Viewing maintenance requests...")

    def updateRequestStatus(self, request_id: int, status: str):
        print(f"Updating request {request_id} to status '{status}' located at {self.location}")
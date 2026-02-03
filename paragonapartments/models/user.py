import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.user_repository as user_repo
import database_operations.repos.location_repository as location_repo
import database_operations.repos.apartment_repository as apartment_repo



def create_user(username: str, user_type: str, location: str = ""):
    """Factory function to create the appropriate user class based on user type"""
    user_type_lower = user_type.lower().replace(" ", "")
    
    if user_type_lower == "administrator" or user_type_lower == "admin":
        return Administrator(username, location)
    elif user_type_lower == "manager":
        return Manager(username, location)
    elif user_type_lower == "financemanager" or user_type_lower == "finance":
        return FinanceManager(username, location)
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

    def change_password(self, values):
        """Change the user's password."""
        old_password = values.get('Old Password', '')
        new_password = values.get('New Password', '')

        success = user_repo.change_password(self.username, old_password, new_password)

        if success:
            return True
        else:
            return "Failed to change password. Please check your old password."

    def load_homepage_content(self, home_page):
        """Initialize and display home page content."""
        # Centered content wrapper
        top_content = pe.content_container(parent=home_page, anchor="nw", fill="x", marginy=(10, 0))

        ctk.CTkLabel(
            top_content, 
            text=self.username + (f" - {self.location}" if self.location else ""), 
            font=("Arial", 24)
        ).pack(side="left", padx=15)

        ctk.CTkLabel(
            top_content, 
            text=self.role + " Dashboard",
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

        _, open_popup = pe.popup_card(home_page, title="Change Password", small=True, generate_button=False)

        def setup_popup():
            content = open_popup()

            fields = [
                {'name': 'Old Password', 'type': 'text', 'subtype': 'password', 'required': True},
                {'name': 'New Password', 'type': 'text', 'subtype': 'password', 'required': True},
            ]
            pe.form_element(content, fields, name="Change Password", submit_text="Change Password", on_submit=self.change_password, small=True)


        ctk.CTkButton(
            home_page, 
            text="Change password",
            bg_color="transparent",
            fg_color="transparent",
            hover_color=("gray90", "gray20"),
            text_color=("black", "white"),
            height=12,
            width=10,
            command=setup_popup,
            font=("Arial", 10),
        ).pack(anchor="ne", padx=15, pady=0)


class Manager(User):
    """Manager user with business-wide access and control."""
    
    def __init__(self, username: str, location: str = None):
        super().__init__(username, role="Manager", location=location)

    def view_apartment_occupancy(self, location: str):
        """
        View apartment occupancy for a specific location or all locations.
        
        Args:
            location (str): City name to filter by, or "all" for all locations
        
        Returns:
            int: Number of occupied apartments
        """
        occupied_count = apartment_repo.get_all_occupancy(location)
        if location and location.lower() != "all":
            print(f"Occupied apartments in {location}: {occupied_count}")
        else:
            print(f"Total occupied apartments: {occupied_count}")
        return occupied_count


    def generate_reports(self, location: str):
        """Generate performance reports for a location."""
        print("Generating performance report...")

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

    def edit_account(self, user_data, values):
        """Edit an existing user account's role and location."""
        user_id = user_data.get('user_ID', None)

        username = values.get('username', '')
        role = values.get('role', '')
        location = values.get('city', None)
        
        # Handle "None" string from dropdown
        if location and location != "None":
            location_id = location_repo.get_location_id_by_city(location)
        else:
            location_id = None

        try:
            user_repo.update_user(user_id, username=username, role=role, location_ID=location_id)
            return True  # Success
        except Exception as e:
            return f"Failed to edit account: {str(e)}"

    def delete_account(self, user_data):
        """Delete an existing user account by username or ID."""

        try:
            if user_data and 'user_ID' in user_data:
                user_repo.delete_user(int(user_data['user_ID']))
            else:
                return "No valid user identifier provided."

            return True  # Success
        except Exception as e:
            return f"Failed to delete account: {str(e)}"

    def expand_business(self, new_location: str):
        """Expand business to a new location."""
        city = new_location.get('City', '')
        address = new_location.get('Address', '')

        try:
            location_repo.create_location(city, address)
            return True  # Success
        except Exception as e:
            return f"Failed to add location: {str(e)}"
    
    def edit_location(self, location_data, values):
        """Edit an existing location's city and address."""
        location_id = location_data.get('location_ID', None)

        city = values.get('city', '')
        address = values.get('address', '')

        try:
            location_repo.update_location(location_id, city=city, address=address)
            return True  # Success
        except Exception as e:
            return f"Failed to edit location: {str(e)}"
        
    def delete_location(self, location_data):
        """Delete an existing location by ID."""

        try:
            if location_data and 'location_ID' in location_data:
                location_repo.delete_location(int(location_data['location_ID']))
            else:
                return "No valid location identifier provided."

            return True  # Success
        except Exception as e:
            return f"Failed to delete location: {str(e)}"

    def add_apartment(self, apartment_data):
        """Add a new apartment to the system."""
        location = apartment_data.get('Location', '')
        apartment_address = apartment_data.get('Apartment Address', '')
        number_of_beds = apartment_data.get('Number of Beds', 0)
        monthly_rent = apartment_data.get('Monthly Rent', 0)
        status = apartment_data.get('Status', 'Vacant')

        occupied = 1 if status.lower() == "occupied" else 0

        try:
            location_id = location_repo.get_location_id_by_city(location)
            apartment_repo.create_apartment(location_id, apartment_address, number_of_beds, monthly_rent, occupied)
            return True  # Success
        except Exception as e:
            return f"Failed to add apartment: {str(e)}"

    def delete_apartment(self, apartment_data):
        """Delete an existing apartment by ID."""

        try:
            if apartment_data and 'apartment_ID' in apartment_data:
                apartment_repo.delete_apartment(int(apartment_data['apartment_ID']))
            else:
                return "No valid apartment identifier provided."

            return True  # Success
        except Exception as e:
            return f"Failed to delete apartment: {str(e)}"
        
    def edit_apartment(self, apartment_data, values):
        """Edit an existing apartment's details."""
        apartment_id = apartment_data.get('apartment_ID', None)

        location = values.get('city', '')
        apartment_address = values.get('apartment_address', '')
        number_of_beds = values.get('number_of_beds', 0)
        monthly_rent = values.get('monthly_rent', 0)
        status = values.get('status', 'Vacant')

        occupied = 1 if status.lower() == "occupied" else 0

        try:
            location_id = location_repo.get_location_id_by_city(location)
            if location_id is None:
                return "Invalid location specified."
            apartment_repo.update_apartment(
                apartment_id,
                location_ID=location_id,
                apartment_address=apartment_address,
                number_of_beds=number_of_beds,
                monthly_rent=monthly_rent,
                occupied=occupied
            )
            return True  # Success
        except Exception as e:
            return f"Failed to edit apartment: {str(e)}"


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
        
        # Get all cities for dropdown
        cities = ['All Locations'] + location_repo.get_all_cities()
        
        # Create dropdown
        location_dropdown = ctk.CTkComboBox(
            occupancy_card,
            values=cities,
            width=200,
            font=("Arial", 14)
        )
        location_dropdown.set("All Locations")
        location_dropdown.pack(pady=10, padx=20)
        
        # Create result label (initially hidden)
        result_label = ctk.CTkLabel(
            occupancy_card,
            text="",
            font=("Arial", 16, "bold"),
            text_color="#3B8ED0"
        )
        result_label.pack(pady=10, padx=20)
        
        # Function to update display
        def update_occupancy_display():
            location = "all" if location_dropdown.get() == "All Locations" else location_dropdown.get()
            occupied_count = self.view_apartment_occupancy(location)
            total_count = apartment_repo.get_total_apartments(location)
            available_count = total_count - occupied_count
            
            if location == "all":
                result_label.configure(
                    text=f"Occupied: {occupied_count} | Available: {available_count} | Total: {total_count}"
                )
            else:
                result_label.configure(
                    text=f"{location} - Occupied: {occupied_count} | Available: {available_count} | Total: {total_count}"
                )
        
        # Create view button
        pe.action_button(
            occupancy_card,
            text="View Occupancy",
            command=update_occupancy_display
        )

        # Create graph popup button
        button, open_popup_func = pe.popup_card(
            occupancy_card,
            title="Apartment Occupancy Graph",
            button_text="Show Occupancy Graph",
            small=False,
            button_size="small"
        )

        def setup_graph_popup():
            content = open_popup_func()
            location = "all" if location_dropdown.get() == "All Locations" else location_dropdown.get()
            apartment_repo.create_occupancy_graph(content, location)

        button.configure(command=setup_graph_popup)

    def load_account_content(self, row):
        accounts_card = pe.function_card(row, "Manage Accounts", side="left")

        fields = [
            {'name': 'Username', 'type': 'text', 'required': True},
            {'name': 'Role', 'type': 'dropdown', 'options': ['Admin', 'Manager', 'Finance Manager', 'Frontdesk', 'Maintenance'], 'required': True},
            {'name': 'Password', 'type': 'text', 'required': True},
            {'name': 'Location', 'type': 'dropdown', 'options': ['None'] + location_repo.get_all_cities(), 'required': False}
        ]

        pe.form_element(accounts_card, fields, name="Create", submit_text="Create Account", on_submit=self.create_account, small=True)

        # Create the popup with a button
        button, open_popup_func = pe.popup_card(
            accounts_card, 
            button_text="Edit Accounts", 
            title="Edit Accounts",
            button_size="small"
        )

        def setup_popup():
            content = open_popup_func()

            columns = [
                {'name': 'ID', 'key': 'user_ID', 'width': 80, 'editable': False},
                {'name': 'Username', 'key': 'username', 'width': 200},
                {'name': 'Location', 'key': 'city', 'width': 200},
                {'name': 'Role', 'key': 'role', 'width': 150}
            ]

            def get_data():
                return user_repo.get_all_users()

            pe.data_table(
                content, 
                columns, 
                editable=True, 
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_account,
                on_update=self.edit_account
            )

        button.configure(command=setup_popup)

    def load_report_content(self, row):
        reports_card = pe.function_card(row, "Performance Reports", side="left")

        # Get all cities for dropdown
        cities = ['All Locations'] + location_repo.get_all_cities()
        
        # Create dropdown
        location_dropdown = ctk.CTkComboBox(
            reports_card,
            values=cities,
            width=200,
            font=("Arial", 14)
        )
        location_dropdown.set("All Locations")
        location_dropdown.pack(pady=10, padx=20)
        
        # Create result label
        result_label = ctk.CTkLabel(
            reports_card,
            text="",
            font=("Arial", 16, "bold"),
            text_color="#3B8ED0"
        )
        result_label.pack(pady=10, padx=20)
        
        # Function to update display
        def update_performance_display():
            location = "all" if location_dropdown.get() == "All Locations" else location_dropdown.get()
            actual_revenue = apartment_repo.get_monthly_revenue(location)
            potential_revenue = apartment_repo.get_potential_revenue(location)
            lost_revenue = potential_revenue - actual_revenue
            
            if location == "all":
                result_label.configure(
                    text=f"Actual: £{actual_revenue:,.2f} | Lost: £{lost_revenue:,.2f} | Potential: £{potential_revenue:,.2f}"
                )
            else:
                result_label.configure(
                    text=f"{location} - Actual: £{actual_revenue:,.2f} | Lost: £{lost_revenue:,.2f} | Potential: £{potential_revenue:,.2f}"
                )
        
        # Create view button
        pe.action_button(
            reports_card,
            text="View Performance",
            command=update_performance_display
        )

        # Create graph popup button
        button, open_popup_func = pe.popup_card(
            reports_card,
            title="Performance Report Graph",
            button_text="Show Performance Graph",
            small=False,
            button_size="small"
        )

        def setup_performance_graph_popup():
            content = open_popup_func()
            location = "all" if location_dropdown.get() == "All Locations" else location_dropdown.get()
            apartment_repo.create_performance_graph(content, location)

        button.configure(command=setup_performance_graph_popup)

    def load_business_expansion_content(self, row):
        expand_card = pe.function_card(row, "Expand Business", side="top")

        fields = [
            {'name': 'City', 'type': 'text', 'required': True},
            {'name': 'Address', 'type': 'text', 'required': True},
        ]

        pe.form_element(expand_card, fields, name="Add Location", submit_text="Add", on_submit=self.expand_business, small=True)

        # Create the popup with a button
        button, open_popup_func = pe.popup_card(
            expand_card, 
            button_text="Edit Locations", 
            title="Edit Locations",
            button_size="small"
        )

        def setup_popup():
            content = open_popup_func()

            columns = [
                {'name': 'ID', 'key': 'location_ID', 'width': 80, 'editable': False},
                {'name': 'City', 'key': 'city', 'width': 200},
                {'name': 'Address', 'key': 'address', 'width': 200}
            ]

            def get_data():
                return location_repo.get_all_locations()

            pe.data_table(
                content, 
                columns, 
                editable=True, 
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_location,
                on_update=self.edit_location
            )

        button.configure(command=setup_popup)

        fields = [
            {'name': 'Location', 'type': 'dropdown', 'options': location_repo.get_all_cities(), 'required': True},
            {'name': 'Apartment Address', 'type': 'text', 'required': True},
            {'name': 'Number of Beds', 'type': 'text', 'subtype': 'number', 'required': True},
            {'name': 'Monthly Rent', 'type': 'text', 'subtype': 'currency', 'required': True},
            {'name': 'Status', 'type': 'dropdown', 'options': ["Vacant", "Occupied"], 'required': True},
        ]

        pe.form_element(expand_card, fields, name="Add Apartment", submit_text="Add", on_submit=self.add_apartment, small=True, field_per_row=5)

        # Create the popup with a button
        button, open_popup_func = pe.popup_card(
            expand_card, 
            button_text="Edit Apartments", 
            title="Edit Apartments",
            button_size="small"
        )

        def setup_popup():
            content = open_popup_func()

            columns = [
                {'name': 'ID', 'key': 'apartment_ID', 'width': 80, 'editable': False},
                {'name': 'Location', 'key': 'city', 'width': 150},
                {'name': 'Address', 'key': 'apartment_address', 'width': 150},
                {'name': 'Beds', 'key': 'number_of_beds', 'width': 80},
                {'name': 'Monthly Rent', 'key': 'monthly_rent', 'width': 120},
                {'name': 'Status', 'key': 'status', 'width': 100}
            ]

            def get_data():
                return apartment_repo.get_all_apartments()

            pe.data_table(
                content, 
                columns, 
                editable=True, 
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_apartment,
                on_update=self.edit_apartment
            )

        button.configure(command=setup_popup)


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
    
    def __init__(self, username: str, location: str = None):
        super().__init__(username, role="Finance Manager", location=location)

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
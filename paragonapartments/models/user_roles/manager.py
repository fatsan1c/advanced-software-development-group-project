import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.user_repository as user_repo
import database_operations.repos.location_repository as location_repo
import database_operations.repos.apartment_repository as apartment_repo
from models.user import User


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

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

# ============================= v Manager functions v  =====================================
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

    # unused for now. May be used in future for more reports or graphs.
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
            # Database operation
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
            # Attempt to delete by ID otherwise return error
            if user_data and 'user_ID' in user_data:
                user_repo.delete_user(int(user_data['user_ID']))
            else:
                return "No valid user identifier provided."

            return True  # Success
        except Exception as e:
            return f"Failed to delete account: {str(e)}"

    def expand_business(self, new_location: str):
        """Expand business to a new location."""
        # Add new location to database
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
            # Attempt to delete by ID otherwise return error
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

        # Convert status to occupied flag
        occupied = 1 if status.lower() == "occupied" else 0

        try:
            # Get location ID from city name
            location_id = location_repo.get_location_id_by_city(location)
            # create apartment in database
            apartment_repo.create_apartment(location_id, apartment_address, number_of_beds, monthly_rent, occupied)
            return True  # Success
        except Exception as e:
            return f"Failed to add apartment: {str(e)}"

    def delete_apartment(self, apartment_data):
        """Delete an existing apartment by ID."""

        try:
            # Attempt to delete by ID otherwise return error
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

        # Convert status to occupied flag
        occupied = 1 if status.lower() == "occupied" else 0

        try:
            # Get location ID from city name
            location_id = location_repo.get_location_id_by_city(location)
            # handle case where location is not found
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
# ============================= ^ Manager functions ^ =====================================

# ============================= v Homepage UI Content v =====================================
    def load_homepage_content(self, home_page):
        """Load Manager-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)

        container = pe.scrollable_container(parent=home_page)

        # First row - 2 cards
        row1 = pe.row_container(parent=container)
        
        # Display how many appartments are occupied vs available for each location, with option to view graph of occupancy trends over time
        self.load_occupancy_content(row1)

        # Manage staff user accounts - create, edit, delete accounts with role and location assignment
        self.load_account_content(row1)

        # Second row - full width card
        row2 = pe.row_container(parent=container)

        # Display financial performance reports for each location and overall business
        self.load_report_content(row2)

        # Third row - full width card
        row3 = pe.row_container(parent=container)
        
        # Allow manager to add new locations and apartments to expand the business
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
        # Set default value to "All Locations"
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
        def update_occupancy_display(choice=None):
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
        
        update_occupancy_display()  # Auto-update when loading the page
        location_dropdown.configure(command=update_occupancy_display)

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

        # Choose field for creating new account form 
        # - username, role (dropdown), password, location (dropdown)
        fields = [
            {'name': 'Username', 'type': 'text', 'required': True},
            {'name': 'Role', 'type': 'dropdown', 'options': ['Admin', 'Manager', 'Finance Manager', 'Frontdesk', 'Maintenance'], 'required': True},
            {'name': 'Password', 'type': 'text', 'required': True},
            {'name': 'Location', 'type': 'dropdown', 'options': ['None'] + location_repo.get_all_cities(), 'required': False}
        ]

        # create form for creating new accounts with above fields
        pe.form_element(accounts_card, fields, name="Create", submit_text="Create Account", on_submit=self.create_account, small=True)

        # Create a popup with a button to edit existing accounts
        button, open_popup_func = pe.popup_card(
            accounts_card, 
            button_text="Edit Accounts", 
            title="Edit Accounts",
            button_size="small"
        )

        def setup_popup():
            content = open_popup_func()

            # Define columns for user data table
            columns = [
                {'name': 'ID', 'key': 'user_ID', 'width': 80, 'editable': False},
                {'name': 'Username', 'key': 'username', 'width': 200},
                {'name': 'Location', 'key': 'city', 'width': 200},
                {'name': 'Role', 'key': 'role', 'width': 150}
            ]

            # Function to fetch user data for the table
            def get_data():
                return user_repo.get_all_users()

            # Create editable and deletable data table for user accounts
            pe.data_table(
                content, 
                columns, 
                editable=True, 
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_account,
                on_update=self.edit_account,
                render_batch_size=20,
                page_size=10,
                scrollable=False
            )

        # Set the button command to open the popup with the user accounts table
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
        # Set default value to "All Locations"
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
        def update_performance_display(choice=None):
            location = "all" if location_dropdown.get() == "All Locations" else location_dropdown.get()
            actual_revenue = apartment_repo.get_monthly_revenue(location)
            potential_revenue = apartment_repo.get_potential_revenue(location)
            lost_revenue = potential_revenue - actual_revenue
            
            # Format the revenue numbers
            if location == "all":
                result_label.configure(
                    text=f"Actual: £{actual_revenue:,.2f} | Lost: £{lost_revenue:,.2f} | Potential: £{potential_revenue:,.2f}"
                )
            else:
                result_label.configure(
                    text=f"{location} - Actual: £{actual_revenue:,.2f} | Lost: £{lost_revenue:,.2f} | Potential: £{potential_revenue:,.2f}"
                )
        
        update_performance_display()  # Auto-update when loading the page
        location_dropdown.configure(command=update_performance_display)

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

        # Define fields for adding a new location
        fields = [
            {'name': 'City', 'type': 'text', 'required': True},
            {'name': 'Address', 'type': 'text', 'required': True},
        ]

        # Create form for adding new location with above fields
        pe.form_element(expand_card, fields, name="Add Location", submit_text="Add", on_submit=self.expand_business, small=True)

        # Create a popup to edit existing locations with a data table
        button, open_popup_func = pe.popup_card(
            expand_card, 
            button_text="Edit Locations", 
            title="Edit Locations",
            button_size="small"
        )

        def setup_popup():
            content = open_popup_func()

            # Define columns for location data table
            columns = [
                {'name': 'ID', 'key': 'location_ID', 'width': 80, 'editable': False},
                {'name': 'City', 'key': 'city', 'width': 200},
                {'name': 'Address', 'key': 'address', 'width': 200}
            ]

            # Function to fetch location data for the table
            def get_data():
                return location_repo.get_all_locations()

            # Create editable and deletable data table for locations
            pe.data_table(
                content, 
                columns, 
                editable=True, 
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_location,
                on_update=self.edit_location,
                scrollable=False,
                page_size=9
            )

        # Set the button command to open the popup with the locations table
        button.configure(command=setup_popup)

        # Define fields for adding a new apartment
        fields = [
            {'name': 'Location', 'type': 'dropdown', 'options': location_repo.get_all_cities(), 'required': True},
            {'name': 'Apartment Address', 'type': 'text', 'required': True},
            {'name': 'Number of Beds', 'type': 'text', 'subtype': 'number', 'required': True},
            {'name': 'Monthly Rent', 'type': 'text', 'subtype': 'currency', 'required': True},
            {'name': 'Status', 'type': 'dropdown', 'options': ["Vacant", "Occupied"], 'required': True},
        ]

        pe.form_element(expand_card, fields, name="Add Apartment", submit_text="Add", on_submit=self.add_apartment, small=True, field_per_row=5)

        # Create a popup to edit existing apartments with a data table
        button, open_popup_func = pe.popup_card(
            expand_card, 
            button_text="Edit Apartments", 
            title="Edit Apartments",
            button_size="small"
        )

        def setup_popup():
            content = open_popup_func()

            # Filter dropdown
            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 0))

            cities = ["All Locations"] + location_repo.get_all_cities()
            location_dropdown = ctk.CTkComboBox(header, values=cities, width=220, font=("Arial", 13))
            location_dropdown.set("All Locations")
            location_dropdown.pack(side="left")

            # Define columns for apartment data table
            columns = [
                {'name': 'ID', 'key': 'apartment_ID', 'width': 80, 'editable': False},
                {'name': 'Location', 'key': 'city', 'width': 150},
                {'name': 'Address', 'key': 'apartment_address', 'width': 150},
                {'name': 'Beds', 'key': 'number_of_beds', 'width': 80},
                {'name': 'Monthly Rent', 'key': 'monthly_rent', 'width': 120, "format": "currency"},
                {'name': 'Status', 'key': 'status', 'width': 100}
            ]

            # Function to fetch apartment data for the table
            def get_data():
                location = location_dropdown.get()
                return apartment_repo.get_all_apartments(location=location)

            # Create editable and deletable data table for apartments
            _, refresh_table = pe.data_table(
                content, 
                columns, 
                editable=True, 
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_apartment,
                on_update=self.edit_apartment,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=9,
                scrollable=False
            )

            # Top refresh button next to the dropdown
            ctk.CTkButton(
                header,
                text="⟳ Refresh",
                command=refresh_table,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25")
            ).pack(side="left", padx=(12, 0))

            # Optional: auto-refresh when changing city
            refresh_timer = {"id": None}
            def schedule_refresh(_choice=None):
                if refresh_timer["id"] is not None:
                    try:
                        content.after_cancel(refresh_timer["id"])
                    except Exception:
                        pass
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_timer["id"] = content.after(150, refresh_table)

            location_dropdown.configure(command=schedule_refresh)

        # Set the button command to open the popup with the apartments table
        button.configure(command=setup_popup)
# ============================= ^ Homepage UI Content ^ =====================================
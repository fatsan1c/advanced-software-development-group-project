import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.user_repository as user_repo
import database_operations.repos.location_repository as location_repo
import database_operations.repos.apartment_repository as apartment_repo
from models.user import User


class Administrator(User):
    """Administrator with location-specific management capabilities."""
    
    def __init__(self, username: str, location: str = ""):
        super().__init__(username, role="Administrator", location=location)

# ============================= v Admin functions v  =====================================
    def view_apartment_occupancy(self):
        """View apartment occupancy for this administrator's location."""
        try:
            occupied_count = apartment_repo.get_all_occupancy(self.location)
            print(f"Occupied apartments in {self.location}: {occupied_count}")
            return occupied_count
        except Exception as e:
            print(f"Error retrieving occupancy data: {e}")
            return 0

    def create_account(self, values):
        """Create a new user account at this administrator's location."""
        username = values.get('Username', '')
        role = values.get('Role', '')
        password = values.get('Password', '')
        
        # Get location ID for this administrator's location
        location_id = location_repo.get_location_id_by_city(self.location)

        try:
            # Create user with administrator's location
            user_repo.create_user(username, password, role, location_id)
            return True  # Success
        except Exception as e:
            return f"Failed to create account: {str(e)}"

    def edit_account(self, user_data, values):
        """Edit an existing user account at this administrator's location."""
        user_id = user_data.get('user_ID', None)
        username = values.get('username', '')
        role = values.get('role', '')
        
        # Keep the location as administrator's location (cannot change)
        location_id = location_repo.get_location_id_by_city(self.location)

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

    def add_apartment(self, apartment_data):
        """Add a new apartment at this administrator's location."""
        apartment_address = apartment_data.get('Apartment Address', '')
        number_of_beds = apartment_data.get('Number of Beds', 0)
        monthly_rent = apartment_data.get('Monthly Rent', 0)
        status = apartment_data.get('Status', 'Vacant')

        # Convert status to occupied flag
        occupied = 1 if status.lower() == "occupied" else 0

        try:
            # Get location ID from administrator's location
            location_id = location_repo.get_location_id_by_city(self.location)
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
        """Edit an existing apartment's details at this location."""
        apartment_id = apartment_data.get('apartment_ID', None)
        apartment_address = values.get('apartment_address', '')
        number_of_beds = values.get('number_of_beds', 0)
        monthly_rent = values.get('monthly_rent', 0)
        status = values.get('status', 'Vacant')

        # Convert status to occupied flag
        occupied = 1 if status.lower() == "occupied" else 0

        try:
            # Get location ID from administrator's location
            location_id = location_repo.get_location_id_by_city(self.location)
            
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
# ============================= ^ Admin functions ^ =====================================
    
# ============================= v Homepage UI Content v =====================================
    def load_homepage_content(self, home_page):
        """Load Administrator-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)

        container = pe.scrollable_container(parent=home_page)

        # First row - 2 cards
        row1 = pe.row_container(parent=container)
        
        # Display apartment occupancy for this location
        self.load_occupancy_content(row1)

        # Manage staff user accounts at this location
        self.load_account_content(row1)

        # Second row - full width card
        row2 = pe.row_container(parent=container)

        # Display financial performance reports for this location
        self.load_reports_content(row2)

        # Third row - full width card
        row3 = pe.row_container(parent=container)
        
        # Manage apartments at this location
        self.load_apartment_content(row3)

    def load_occupancy_content(self, row):
        occupancy_card = pe.function_card(row, f"Apartment Occupancy - {self.location}", side="left")
        
        # Create result label
        result_label = ctk.CTkLabel(
            occupancy_card,
            text="",
            font=("Arial", 16, "bold"),
            text_color="#3B8ED0"
        )
        result_label.pack(pady=10, padx=20)
        
        # Function to update display
        def update_occupancy_display():
            try:
                occupied_count = self.view_apartment_occupancy()
                total_count = apartment_repo.get_total_apartments(self.location)
                available_count = total_count - occupied_count
                
                result_label.configure(
                    text=f"Occupied: {occupied_count} | Available: {available_count} | Total: {total_count}"
                )
            except Exception as e:
                result_label.configure(text=f"Error loading data: {str(e)}", text_color="red")
        
        update_occupancy_display()  # Auto-update when loading the page

        # Create graph popup button
        button, open_popup_func = pe.popup_card(
            occupancy_card,
            title=f"Apartment Occupancy Graph - {self.location}",
            button_text="Show Occupancy Graph",
            small=False,
            button_size="small"
        )

        def setup_graph_popup():
            content = open_popup_func()
            apartment_repo.create_occupancy_graph(content, self.location)

        button.configure(command=setup_graph_popup)
        
    def load_account_content(self, row):
        accounts_card = pe.function_card(row, f"Manage Accounts - {self.location}", side="left")

        # Choose fields for creating new account form 
        # Only username, role, and password (location is fixed to administrator's location)
        fields = [
            {'name': 'Username', 'type': 'text', 'required': True},
            {'name': 'Role', 'type': 'dropdown', 'options': ['Admin', 'Frontdesk', 'Maintenance'], 'required': True},
            {'name': 'Password', 'type': 'text', 'required': True}
        ]

        # create form for creating new accounts with above fields
        pe.form_element(accounts_card, fields, name="Create", submit_text="Create Account", on_submit=self.create_account, small=True)

        # Create a popup with a button to edit existing accounts
        button, open_popup_func = pe.popup_card(
            accounts_card, 
            button_text="Edit Accounts", 
            title=f"Edit Accounts - {self.location}",
            button_size="small"
        )

        def setup_popup():
            content = open_popup_func()

            # Define columns for user data table
            columns = [
                {'name': 'ID', 'key': 'user_ID', 'width': 80, 'editable': False},
                {'name': 'Username', 'key': 'username', 'width': 200},
                {'name': 'Role', 'key': 'role', 'width': 150}
            ]

            # Function to fetch user data for the table (filtered by location)
            def get_data():
                try:
                    all_users = user_repo.get_all_users()
                    # Filter users by administrator's location
                    return [user for user in all_users if user.get('city') == self.location]
                except Exception as e:
                    print(f"Error loading users: {e}")
                    return []

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

    def load_reports_content(self, row):
        reports_card = pe.function_card(row, f"Performance Reports - {self.location}", side="left")
        
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
            try:
                actual_revenue = apartment_repo.get_monthly_revenue(self.location)
                potential_revenue = apartment_repo.get_potential_revenue(self.location)
                lost_revenue = potential_revenue - actual_revenue
                
                result_label.configure(
                    text=f"Actual: £{actual_revenue:,.2f} | Lost: £{lost_revenue:,.2f} | Potential: £{potential_revenue:,.2f}"
                )
            except Exception as e:
                result_label.configure(text=f"Error loading revenue data: {str(e)}", text_color="red")
        
        update_performance_display()  # Auto-update when loading the page

        # Create graph popup button
        button, open_popup_func = pe.popup_card(
            reports_card,
            title=f"Performance Report Graph - {self.location}",
            button_text="Show Performance Graph",
            small=False,
            button_size="small"
        )

        def setup_performance_graph_popup():
            content = open_popup_func()
            apartment_repo.create_performance_graph(content, self.location)

        button.configure(command=setup_performance_graph_popup)

    def load_apartment_content(self, row):
        apartment_card = pe.function_card(row, f"Manage Apartments - {self.location}", side="top")

        # Define fields for adding a new apartment (location is fixed)
        fields = [
            {'name': 'Apartment Address', 'type': 'text', 'required': True},
            {'name': 'Number of Beds', 'type': 'text', 'subtype': 'number', 'required': True},
            {'name': 'Monthly Rent', 'type': 'text', 'subtype': 'currency', 'required': True},
            {'name': 'Status', 'type': 'dropdown', 'options': ["Vacant", "Occupied"], 'required': True},
        ]

        pe.form_element(apartment_card, fields, name="Add Apartment", submit_text="Add", on_submit=self.add_apartment, small=True, field_per_row=4)

        # Create a popup to edit existing apartments with a data table
        button, open_popup_func = pe.popup_card(
            apartment_card, 
            button_text="Edit Apartments", 
            title=f"Edit Apartments - {self.location}",
            button_size="small"
        )

        def setup_popup():
            content = open_popup_func()

            # Define columns for apartment data table
            columns = [
                {'name': 'ID', 'key': 'apartment_ID', 'width': 80, 'editable': False},
                {'name': 'Address', 'key': 'apartment_address', 'width': 200},
                {'name': 'Beds', 'key': 'number_of_beds', 'format': 'number', 'width': 80},
                {'name': 'Monthly Rent', 'key': 'monthly_rent', 'format': 'currency', 'width': 120},
                {'name': 'Status', 'key': 'status', 'width': 100}
            ]

            # Function to fetch apartment data for the table (filtered by location)
            def get_data():
                try:
                    return apartment_repo.get_all_apartments(location=self.location)
                except Exception as e:
                    print(f"Error loading apartments: {e}")
                    return []

            # Create editable and deletable data table for apartments
            pe.data_table(
                content, 
                columns, 
                editable=True, 
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_apartment,
                on_update=self.edit_apartment,
                render_batch_size=20,
                page_size=10,
                scrollable=False
            )

        # Set the button command to open the popup with the apartments table
        button.configure(command=setup_popup)
# ============================= ^ Homepage UI Content ^ =====================================
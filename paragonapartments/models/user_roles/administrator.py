import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.user_repository as user_repo
import database_operations.repos.location_repository as location_repo
import database_operations.repos.apartment_repository as apartment_repo
from models.user import User
from pages.components.config.theme import PRIMARY_BLUE, PRIMARY_BLUE_HOVER, ROUND_BOX, ROUND_BTN, ROUND_INPUT


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
        occupancy_card = pe.function_card(row, f"Apartment Occupancy - {self.location}", side="left", pady=6, padx=8)

        # Top info row: occupancy badge
        info_row = ctk.CTkFrame(occupancy_card, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 6))

        occupancy_badge = pe.info_badge(info_row, "Total units: 0")

        # Stat grid
        stats = pe.stats_grid(occupancy_card)

        occupied_value = pe.stat_card(stats, "Occupied")
        available_value = pe.stat_card(stats, "Available")
        total_value = pe.stat_card(stats, "Total")

        def update_occupancy_display():
            try:
                occupied_count = self.view_apartment_occupancy()
                total_count = apartment_repo.get_total_apartments(self.location)
                available_count = total_count - occupied_count

                occupied_value.configure(text=str(occupied_count))
                available_value.configure(text=str(available_count))
                total_value.configure(text=str(total_count))
                occupancy_badge.configure(text=f"Total units: {total_count}")
            except Exception as e:
                print(f"Error loading occupancy data: {e}")

        update_occupancy_display()
        refresh_timer, schedule_refresh = pe.create_debounced_refresh(occupancy_card, update_occupancy_display)

        # Graph popup button
        button, open_popup_func = pe.popup_card(
            occupancy_card,
            title=f"Apartment Occupancy Graph - {self.location}",
            button_text="View Graphs",
            small=False,
            button_size="medium"
        )
        pe.style_primary_button(button)

        def setup_graph_popup():
            content = open_popup_func()
            controls = ctk.CTkFrame(content, fg_color="transparent")
            controls.pack(fill="x", padx=10, pady=(5, 10))
            row_top = ctk.CTkFrame(controls, fg_color="transparent")
            row_top.pack(fill="x")
            ctk.CTkLabel(row_top, text="Grouping:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))
            grouping_dropdown = ctk.CTkComboBox(row_top, values=["Monthly", "Yearly"], width=140, font=("Arial", 13))
            grouping_dropdown.set("Monthly")
            grouping_dropdown.pack(side="left")

            row_dates = ctk.CTkFrame(controls, fg_color="transparent")
            row_dates.pack(fill="x", pady=(10, 0))
            default_range = apartment_repo.get_lease_date_range(self.location, grouping="month")
            default_start, default_end = default_range.get("start_date", ""), default_range.get("end_date", "")

            ctk.CTkLabel(row_dates, text="Start (YYYY-MM-DD):", font=("Arial", 13, "bold")).pack(side="left", padx=(0, 8))
            start_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            start_wrap.pack(side="left")
            start_entry = ctk.CTkEntry(start_wrap, width=140, font=("Arial", 13))
            if default_start:
                start_entry.insert(0, default_start)
            start_entry.pack(side="left")
            ctk.CTkLabel(row_dates, text="End (YYYY-MM-DD):", font=("Arial", 13, "bold")).pack(side="left", padx=(18, 8))
            end_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            end_wrap.pack(side="left")
            end_entry = ctk.CTkEntry(end_wrap, width=140, font=("Arial", 13))
            if default_end:
                end_entry.insert(0, default_end)
            end_entry.pack(side="left")

            ctk.CTkButton(start_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                         command=lambda: pe.open_date_picker(start_entry, content.winfo_toplevel()),
                         fg_color=("gray80", "gray25"), hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))
            ctk.CTkButton(end_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                         command=lambda: pe.open_date_picker(end_entry, content.winfo_toplevel()),
                         fg_color=("gray80", "gray25"), hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))

            def apply_grouping_defaults(gv):
                gv = (gv or "").strip().lower()
                g = "year" if gv.startswith("year") else "month"
                rng = apartment_repo.get_lease_date_range(self.location, grouping=g)
                start_entry.delete(0, "end")
                end_entry.delete(0, "end")
                if rng.get("start_date"):
                    start_entry.insert(0, rng["start_date"])
                if rng.get("end_date"):
                    end_entry.insert(0, rng["end_date"])

            error_label = ctk.CTkLabel(content, text="", font=("Arial", 12), text_color="red", wraplength=900)
            error_label.pack(fill="x", padx=10, pady=(0, 5))
            graph_container = ctk.CTkFrame(content, fg_color="transparent")
            graph_container.pack(fill="both", expand=True)

            def render_graph():
                for w in graph_container.winfo_children():
                    w.destroy()
                error_label.configure(text="")
                try:
                    grouping = "year" if grouping_dropdown.get() == "Yearly" else "month"
                    start_date = start_entry.get().strip() or None
                    end_date = end_entry.get().strip() or None
                    apartment_repo.create_occupancy_trend_graph(graph_container, location=self.location,
                                                               start_date=start_date, end_date=end_date,
                                                               grouping=grouping)
                except Exception as e:
                    error_label.configure(text=f"Error: {str(e)}")

            refresh_btn = ctk.CTkButton(row_top, text="⟳ Refresh", command=render_graph, height=32, width=120,
                                        fg_color=("gray70", "gray30"), hover_color=("gray60", "gray25"))
            refresh_btn.pack(side="left", padx=(18, 0))
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, render_graph)
            def on_grouping_change(choice=None):
                apply_grouping_defaults(grouping_dropdown.get())
                schedule_refresh(choice)
            grouping_dropdown.configure(command=on_grouping_change)
            render_graph()

        button.configure(command=setup_graph_popup)
        
    def load_account_content(self, row):
        accounts_card = pe.function_card(row, f"Manage Accounts - {self.location}", side="left", pady=6, padx=8)

        # Choose fields for creating new account form 
        # Only username, role, and password (location is fixed to administrator's location)
        fields = [
            {'name': 'Username', 'type': 'text', 'required': True},
            {'name': 'Role', 'type': 'dropdown', 'options': ['Admin', 'Frontdesk', 'Maintenance'], 'required': True},
            {'name': 'Password', 'type': 'text', 'required': True}
        ]

        # create form for creating new accounts with above fields
        pe.form_element(
            accounts_card,
            fields,
            name="Create",
            submit_text="Create Account",
            on_submit=self.create_account,
            small=True,
            expand=False,
            fill="x",
            pady=(2, 2),
            submit_button_height=40,
            submit_button_font_size=13,
            input_corner_radius=ROUND_INPUT,
            submit_corner_radius=ROUND_BTN,
            submit_fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
            submit_hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
            submit_text_color=("white", "white"),
        )

        # Create a popup with a button to edit existing accounts
        button, open_popup_func = pe.popup_card(
            accounts_card, 
            button_text="Edit Accounts", 
            title=f"Edit Accounts - {self.location}",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(button)

        def setup_popup():
            content = open_popup_func()

            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            # Define columns for user data table
            columns = [
                {'name': 'ID', 'key': 'user_ID', 'width': 80, 'editable': False},
                {'name': 'Username', 'key': 'username', 'width': 200},
                {'name': 'Role', 'key': 'role', 'width': 150, 'format': 'dropdown', 'options': ['Admin', 'Frontdesk', 'Maintenance']}
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
            _, refresh_table = pe.data_table(
                content, 
                columns, 
                editable=True, 
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_account,
                on_update=self.edit_account,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10,
            )

            pe.create_refresh_button(header, refresh_table, padx=0)

        # Set the button command to open the popup with the user accounts table
        button.configure(command=setup_popup)

    def load_reports_content(self, row):
        reports_card = pe.function_card(row, f"Performance Report - {self.location}", side="top", pady=6, padx=8)

        # Top info row: vacant badge
        info_row = ctk.CTkFrame(reports_card, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 6))

        vacant_badge = pe.info_badge(info_row, "Vacant units: 0")

        # Stat grid
        stats = pe.stats_grid(reports_card)
        actual_value = pe.stat_card(stats, "Actual Revenue", "£0.00")
        lost_value = pe.stat_card(stats, "Lost Revenue", "£0.00")
        potential_value = pe.stat_card(stats, "Potential Revenue", "£0.00")

        def update_performance_display():
            try:
                actual_revenue = apartment_repo.get_monthly_revenue(self.location)
                potential_revenue = apartment_repo.get_potential_revenue(self.location)
                lost_revenue = potential_revenue - actual_revenue
                total = apartment_repo.get_total_apartments(self.location)
                occupied = apartment_repo.get_all_occupancy(self.location)
                vacant = total - occupied

                actual_value.configure(text=f"£{actual_revenue:,.2f}")
                lost_value.configure(text=f"£{lost_revenue:,.2f}")
                potential_value.configure(text=f"£{potential_revenue:,.2f}")
                vacant_badge.configure(text=f"Vacant units: {vacant}")
            except Exception as e:
                print(f"Error loading revenue data: {e}")

        update_performance_display()
        refresh_timer, schedule_refresh = pe.create_debounced_refresh(reports_card, update_performance_display)

        button, open_popup_func = pe.popup_card(
            reports_card,
            title=f"Performance Report Graph - {self.location}",
            button_text="View Graphs",
            small=False,
            button_size="medium"
        )
        pe.style_primary_button(button)

        def setup_performance_graph_popup():
            content = open_popup_func()
            controls = ctk.CTkFrame(content, fg_color="transparent")
            controls.pack(fill="x", padx=10, pady=(5, 10))
            row_top = ctk.CTkFrame(controls, fg_color="transparent")
            row_top.pack(fill="x")
            ctk.CTkLabel(row_top, text="Grouping:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))
            grouping_dropdown = ctk.CTkComboBox(row_top, values=["Monthly", "Yearly"], width=140, font=("Arial", 13))
            grouping_dropdown.set("Monthly")
            grouping_dropdown.pack(side="left")

            row_dates = ctk.CTkFrame(controls, fg_color="transparent")
            row_dates.pack(fill="x", pady=(10, 0))
            default_range = apartment_repo.get_lease_date_range(self.location, grouping="month")
            default_start, default_end = default_range.get("start_date", ""), default_range.get("end_date", "")

            ctk.CTkLabel(row_dates, text="Start (YYYY-MM-DD):", font=("Arial", 13, "bold")).pack(side="left", padx=(0, 8))
            start_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            start_wrap.pack(side="left")
            start_entry = ctk.CTkEntry(start_wrap, width=140, font=("Arial", 13))
            if default_start:
                start_entry.insert(0, default_start)
            start_entry.pack(side="left")
            ctk.CTkLabel(row_dates, text="End (YYYY-MM-DD):", font=("Arial", 13, "bold")).pack(side="left", padx=(18, 8))
            end_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            end_wrap.pack(side="left")
            end_entry = ctk.CTkEntry(end_wrap, width=140, font=("Arial", 13))
            if default_end:
                end_entry.insert(0, default_end)
            end_entry.pack(side="left")

            ctk.CTkButton(start_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                         command=lambda: pe.open_date_picker(start_entry, content.winfo_toplevel()),
                         fg_color=("gray80", "gray25"), hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))
            ctk.CTkButton(end_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                         command=lambda: pe.open_date_picker(end_entry, content.winfo_toplevel()),
                         fg_color=("gray80", "gray25"), hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))

            def apply_grouping_defaults(gv):
                gv = (gv or "").strip().lower()
                g = "year" if gv.startswith("year") else "month"
                rng = apartment_repo.get_lease_date_range(self.location, grouping=g)
                start_entry.delete(0, "end")
                end_entry.delete(0, "end")
                if rng.get("start_date"):
                    start_entry.insert(0, rng["start_date"])
                if rng.get("end_date"):
                    end_entry.insert(0, rng["end_date"])

            error_label = ctk.CTkLabel(content, text="", font=("Arial", 12), text_color="red", wraplength=900)
            error_label.pack(fill="x", padx=10, pady=(0, 5))
            graph_container = ctk.CTkFrame(content, fg_color="transparent")
            graph_container.pack(fill="both", expand=True)

            def render_graph():
                for w in graph_container.winfo_children():
                    w.destroy()
                error_label.configure(text="")
                try:
                    grouping = "year" if grouping_dropdown.get() == "Yearly" else "month"
                    start_date = start_entry.get().strip() or None
                    end_date = end_entry.get().strip() or None
                    apartment_repo.create_revenue_trend_graph(graph_container, location=self.location,
                                                             start_date=start_date, end_date=end_date,
                                                             grouping=grouping)
                except Exception as e:
                    error_label.configure(text=f"Error: {str(e)}")

            refresh_btn = ctk.CTkButton(row_top, text="⟳ Refresh", command=render_graph, height=32, width=120,
                                        fg_color=("gray70", "gray30"), hover_color=("gray60", "gray25"))
            refresh_btn.pack(side="left", padx=(18, 0))
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, render_graph)
            def on_grouping_change(choice=None):
                apply_grouping_defaults(grouping_dropdown.get())
                schedule_refresh(choice)
            grouping_dropdown.configure(command=on_grouping_change)
            render_graph()

        button.configure(command=setup_performance_graph_popup)

    def load_apartment_content(self, row):
        apartment_card = pe.function_card(row, f"Manage Apartments - {self.location}", side="top", pady=6, padx=8)

        # Define fields for adding a new apartment (location is fixed)
        fields = [
            {'name': 'Apartment Address', 'type': 'text', 'required': True},
            {'name': 'Number of Beds', 'type': 'text', 'subtype': 'number', 'required': True},
            {'name': 'Monthly Rent', 'type': 'text', 'subtype': 'currency', 'required': True},
            {'name': 'Status', 'type': 'dropdown', 'options': ["Vacant", "Occupied"], 'required': True},
        ]

        pe.form_element(
            apartment_card,
            fields,
            name="Add Apartment",
            submit_text="Add",
            on_submit=self.add_apartment,
            small=True,
            field_per_row=4,
            expand=False,
            fill="x",
            pady=(2, 2),
            submit_button_height=40,
            submit_button_font_size=13,
            input_corner_radius=ROUND_INPUT,
            submit_corner_radius=ROUND_BTN,
            submit_fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
            submit_hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
            submit_text_color=("white", "white"),
        )

        # Create a popup to edit existing apartments with a data table
        button, open_popup_func = pe.popup_card(
            apartment_card, 
            button_text="Edit Apartments", 
            title=f"Edit Apartments - {self.location}",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(button)

        def setup_popup():
            content = open_popup_func()

            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            # Define columns for apartment data table
            columns = [
                {'name': 'ID', 'key': 'apartment_ID', 'width': 80, 'editable': False},
                {'name': 'Address', 'key': 'apartment_address', 'width': 200},
                {'name': 'Beds', 'key': 'number_of_beds', 'format': 'number', 'width': 80},
                {'name': 'Monthly Rent', 'key': 'monthly_rent', 'format': 'currency', 'width': 120},
                {'name': 'Status', 'key': 'status', 'width': 100, 'format': 'dropdown', 'options': ["Vacant", "Occupied"]}
            ]

            # Function to fetch apartment data for the table (filtered by location)
            def get_data():
                try:
                    return apartment_repo.get_all_apartments(location=self.location)
                except Exception as e:
                    print(f"Error loading apartments: {e}")
                    return []

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
                page_size=10,
            )

            pe.create_refresh_button(header, refresh_table, padx=0)

        # Set the button command to open the popup with the apartments table
        button.configure(command=setup_popup)
# ============================= ^ Homepage UI Content ^ =====================================
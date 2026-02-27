import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.user_repository as user_repo
import database_operations.repos.location_repository as location_repo
import database_operations.repos.apartment_repository as apartment_repo
from models.user import User
from datetime import datetime
from pages.components.config.theme import PRIMARY_BLUE, PRIMARY_BLUE_HOVER, ROUND_BOX, ROUND_BTN, ROUND_INPUT

try:
    from tkcalendar import Calendar
except Exception:
    Calendar = None


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
        try:
            occupied_count = apartment_repo.get_all_occupancy(location)
            if location and location.lower() != "all":
                print(f"Occupied apartments in {location}: {occupied_count}")
            else:
                print(f"Total occupied apartments: {occupied_count}")
            return occupied_count
        except Exception as e:
            print(f"Error retrieving occupancy data: {e}")
            return 0

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

        # First row - Performance Reports at top (full width, finance-style)
        row1 = pe.row_container(parent=container)
        self.load_report_content(row1, side="top")

        # Second row - Occupancy + Accounts
        row2 = pe.row_container(parent=container)
        self.load_occupancy_content(row2)
        self.load_account_content(row2)

        # Third row - Expand Business
        row3 = pe.row_container(parent=container)
        self.load_business_expansion_content(row3)

    def load_occupancy_content(self, row):
        occupancy_card = pe.function_card(row, "Apartment Occupancy", side="left", pady=6, padx=8)

        # Top info row: occupancy badge (left) + location selector (right) - match Performance Reports
        info_row = ctk.CTkFrame(occupancy_card, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 6))

        occupancy_badge = pe.info_badge(info_row, "Total units: 0")

        location_dropdown = pe.location_dropdown_with_label(info_row)

        # Stat grid - match Performance Reports layout
        stats = pe.stats_grid(occupancy_card)

        occupied_value = pe.stat_card(stats, "Occupied")
        available_value = pe.stat_card(stats, "Available")
        total_value = pe.stat_card(stats, "Total")

        def update_occupancy_display(choice=None):
            location = "all" if location_dropdown.get() == "All Locations" else location_dropdown.get()
            occupied_count = self.view_apartment_occupancy(location)
            total_count = apartment_repo.get_total_apartments(location)
            available_count = total_count - occupied_count

            occupied_value.configure(text=str(occupied_count))
            available_value.configure(text=str(available_count))
            total_value.configure(text=str(total_count))
            occupancy_badge.configure(text=f"Total units: {total_count}")

        update_occupancy_display()
        refresh_timer, schedule_refresh = pe.create_debounced_refresh(occupancy_card, update_occupancy_display)
        location_dropdown.configure(command=schedule_refresh)

        # Graph popup button - styled like finance
        button, open_popup_func = pe.popup_card(
            occupancy_card,
            title="Apartment Occupancy Graph",
            button_text="View Graphs",
            small=False,
            button_size="medium"
        )
        pe.style_primary_button(button)

        def _selected_location(val):
            return "all" if (val or "") == "All Locations" else (val or "all")

        def setup_graph_popup():
            content = open_popup_func()
            controls = ctk.CTkFrame(content, fg_color="transparent")
            controls.pack(fill="x", padx=10, pady=(5, 10))

            row_top = ctk.CTkFrame(controls, fg_color="transparent")
            row_top.pack(fill="x")
            ctk.CTkLabel(row_top, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))
            popup_cities = ["All Locations"] + location_repo.get_all_cities()
            popup_location_dropdown = ctk.CTkComboBox(row_top, values=popup_cities, width=220, font=("Arial", 13))
            popup_location_dropdown.set(location_dropdown.get() or "All Locations")
            popup_location_dropdown.pack(side="left")
            ctk.CTkLabel(row_top, text="Grouping:", font=("Arial", 14, "bold")).pack(side="left", padx=(18, 8))
            grouping_dropdown = ctk.CTkComboBox(row_top, values=["Monthly", "Yearly"], width=140, font=("Arial", 13))
            grouping_dropdown.set("Monthly")
            grouping_dropdown.pack(side="left")

            row_dates = ctk.CTkFrame(controls, fg_color="transparent")
            row_dates.pack(fill="x", pady=(10, 0))
            loc_for_defaults = _selected_location(popup_location_dropdown.get())
            default_range = apartment_repo.get_lease_date_range(loc_for_defaults, grouping="month")
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
                rng = apartment_repo.get_lease_date_range(_selected_location(popup_location_dropdown.get()), grouping=g)
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
                    try:
                        w.destroy()
                    except Exception:
                        pass
                try:
                    loc = _selected_location(popup_location_dropdown.get())
                    gv = (grouping_dropdown.get() or "Monthly").strip().lower()
                    g = "year" if gv.startswith("year") else "month"
                    apartment_repo.create_occupancy_trend_graph(
                        graph_container, location=loc,
                        start_date=start_entry.get().strip() or None,
                        end_date=end_entry.get().strip() or None,
                        grouping=g)
                    error_label.configure(text="")
                except Exception as e:
                    error_label.configure(text=str(e))

            refresh_btn = ctk.CTkButton(row_top, text="⟳ Refresh", command=render_graph, height=32, width=120,
                                        fg_color=("gray70", "gray30"), hover_color=("gray60", "gray25"))
            refresh_btn.pack(side="left", padx=(18, 0))
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, render_graph)
            popup_location_dropdown.configure(command=schedule_refresh)
            def on_grouping_change(choice=None):
                apply_grouping_defaults(grouping_dropdown.get())
                schedule_refresh(choice)
            grouping_dropdown.configure(command=on_grouping_change)
            render_graph()

        button.configure(command=setup_graph_popup)

    def load_account_content(self, row):
        accounts_card = pe.function_card(row, "Manage Accounts", side="left", pady=6, padx=8)

        try:
            location_options = ['None'] + location_repo.get_all_cities()
        except Exception as e:
            print(f"Error loading locations: {e}")
            location_options = ['None']

        fields = [
            {'name': 'Username', 'type': 'text', 'required': True},
            {'name': 'Role', 'type': 'dropdown', 'options': ['Admin', 'Manager', 'Finance Manager', 'Frontdesk', 'Maintenance'], 'required': True},
            {'name': 'Password', 'type': 'text', 'required': True},
            {'name': 'Location', 'type': 'dropdown', 'options': location_options, 'required': False}
        ]

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

        button, open_popup_func = pe.popup_card(
            accounts_card,
            button_text="Edit Accounts",
            title="Edit Accounts",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(button)

        def setup_popup():
            content = open_popup_func()

            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            columns = [
                {'name': 'ID', 'key': 'user_ID', 'width': 80, 'editable': False},
                {'name': 'Username', 'key': 'username', 'width': 200},
                {'name': 'Location', 'key': 'city', 'width': 200, 'format': 'dropdown', 'options': ['None'] + location_repo.get_all_cities()},
                {'name': 'Role', 'key': 'role', 'width': 150, 'format': 'dropdown', 'options': ['Admin', 'Manager', 'Finance Manager', 'Frontdesk', 'Maintenance']}
            ]

            def get_data():
                try:
                    return user_repo.get_all_users()
                except Exception as e:
                    print(f"Error loading users: {e}")
                    return []

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

        button.configure(command=setup_popup)

    def load_report_content(self, row, side="left"):
        reports_card = pe.function_card(row, "Performance Report", side=side, pady=6, padx=8)

        # Top info row: vacant badge (left) + location selector (right) - match finance layout
        info_row = ctk.CTkFrame(reports_card, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 6))

        vacant_badge = pe.info_badge(info_row, "Vacant units: 0")
        location_dropdown = pe.location_dropdown_with_label(info_row)

        # Stat grid
        stats = pe.stats_grid(reports_card)
        actual_value = pe.stat_card(stats, "Actual Revenue", "£0.00")
        # lost_value = pe.stat_card(stats, "Lost Revenue", "£0.00")
        potential_value = pe.stat_card(stats, "Potential Revenue", "£0.00")

        def update_performance_display(choice=None):
            location = "all" if location_dropdown.get() == "All Locations" else location_dropdown.get()
            actual_revenue = apartment_repo.get_monthly_revenue(location)
            potential_revenue = apartment_repo.get_potential_revenue(location)
            # lost_revenue = potential_revenue - actual_revenue
            total = apartment_repo.get_total_apartments(location)
            occupied = apartment_repo.get_all_occupancy(location)
            vacant = total - occupied

            actual_value.configure(text=f"£{actual_revenue:,.2f}")
            # lost_value.configure(text=f"£{lost_revenue:,.2f}")
            potential_value.configure(text=f"£{potential_revenue:,.2f}")
            vacant_badge.configure(text=f"Vacant units: {vacant}")

        update_performance_display()
        refresh_timer, schedule_refresh = pe.create_debounced_refresh(reports_card, update_performance_display)
        location_dropdown.configure(command=schedule_refresh)

        button, open_popup_func = pe.popup_card(
            reports_card,
            title="Performance Report Graph",
            button_text="View Graphs",
            small=False,
            button_size="medium"
        )
        pe.style_primary_button(button)

        def _sel(val):
            return "all" if (val or "") == "All Locations" else (val or "all")

        def setup_performance_graph_popup():
            content = open_popup_func()
            controls = ctk.CTkFrame(content, fg_color="transparent")
            controls.pack(fill="x", padx=10, pady=(5, 10))
            row_top = ctk.CTkFrame(controls, fg_color="transparent")
            row_top.pack(fill="x")
            ctk.CTkLabel(row_top, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))
            popup_cities = ["All Locations"] + location_repo.get_all_cities()
            popup_location_dropdown = ctk.CTkComboBox(row_top, values=popup_cities, width=220, font=("Arial", 13))
            popup_location_dropdown.set(location_dropdown.get() or "All Locations")
            popup_location_dropdown.pack(side="left")
            ctk.CTkLabel(row_top, text="Grouping:", font=("Arial", 14, "bold")).pack(side="left", padx=(18, 8))
            grouping_dropdown = ctk.CTkComboBox(row_top, values=["Monthly", "Yearly"], width=140, font=("Arial", 13))
            grouping_dropdown.set("Monthly")
            grouping_dropdown.pack(side="left")

            row_dates = ctk.CTkFrame(controls, fg_color="transparent")
            row_dates.pack(fill="x", pady=(10, 0))
            loc_def = _sel(popup_location_dropdown.get())
            default_range = apartment_repo.get_lease_date_range(loc_def, grouping="month")
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
                         command=lambda: pe.open_date_picker(start_entry, content.winfo_toplevel()), fg_color=("gray80", "gray25"),
                         hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))
            ctk.CTkButton(end_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                         command=lambda: pe.open_date_picker(end_entry, content.winfo_toplevel()), fg_color=("gray80", "gray25"),
                         hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))

            def apply_grouping_defaults(gv):
                g = "year" if (gv or "").strip().lower().startswith("year") else "month"
                rng = apartment_repo.get_lease_date_range(_sel(popup_location_dropdown.get()), grouping=g)
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
                    try:
                        w.destroy()
                    except Exception:
                        pass
                try:
                    loc = _sel(popup_location_dropdown.get())
                    gv = (grouping_dropdown.get() or "Monthly").strip().lower()
                    g = "year" if gv.startswith("year") else "month"
                    apartment_repo.create_revenue_trend_graph(
                        graph_container, location=loc,
                        start_date=start_entry.get().strip() or None,
                        end_date=end_entry.get().strip() or None,
                        grouping=g)
                    error_label.configure(text="")
                except Exception as e:
                    error_label.configure(text=str(e))

            refresh_btn = ctk.CTkButton(row_top, text="⟳ Refresh", command=render_graph, height=32, width=120,
                                        fg_color=("gray70", "gray30"), hover_color=("gray60", "gray25"))
            refresh_btn.pack(side="left", padx=(18, 0))
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, render_graph)
            popup_location_dropdown.configure(command=schedule_refresh)
            def on_grouping_change(choice=None):
                apply_grouping_defaults(grouping_dropdown.get())
                schedule_refresh(choice)
            grouping_dropdown.configure(command=on_grouping_change)
            render_graph()

        button.configure(command=setup_performance_graph_popup)

    def load_business_expansion_content(self, row):
        expand_card = pe.function_card(row, "Expand Business", side="top", pady=6, padx=8)

        # Two-column layout: Locations (left) | Apartments (right)
        main_row = ctk.CTkFrame(expand_card, fg_color="transparent")
        main_row.pack(fill="both", expand=True)

        left_col = ctk.CTkFrame(main_row, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right_col = ctk.CTkFrame(main_row, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True, padx=(12, 0))

        # Left column: Add Location + Edit Locations
        location_fields = [
            {'name': 'City', 'type': 'text', 'required': True},
            {'name': 'Address', 'type': 'text', 'required': True},
        ]
        pe.form_element(
            left_col,
            location_fields,
            name="Add Location",
            submit_text="Add",
            on_submit=self.expand_business,
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

        loc_btn, open_loc_popup = pe.popup_card(
            left_col,
            button_text="Edit Locations",
            title="Edit Locations",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(loc_btn)

        def setup_loc_popup():
            content = open_loc_popup()

            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            columns = [
                {'name': 'ID', 'key': 'location_ID', 'width': 80, 'editable': False},
                {'name': 'City', 'key': 'city', 'width': 200},
                {'name': 'Address', 'key': 'address', 'width': 200}
            ]

            def get_data():
                try:
                    return location_repo.get_all_locations()
                except Exception as e:
                    print(f"Error loading locations: {e}")
                    return []

            _, refresh_table = pe.data_table(
                content,
                columns,
                editable=True,
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_location,
                on_update=self.edit_location,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10,
            )

            pe.create_refresh_button(header, refresh_table, padx=0)

        loc_btn.configure(command=setup_loc_popup)

        try:
            location_options = location_repo.get_all_cities()
        except Exception as e:
            print(f"Error loading locations: {e}")
            location_options = []

        apartment_fields = [
            {'name': 'Location', 'type': 'dropdown', 'options': location_options, 'required': True},
            {'name': 'Apartment Address', 'type': 'text', 'required': True},
            {'name': 'Number of Beds', 'type': 'text', 'subtype': 'number', 'required': True},
            {'name': 'Monthly Rent', 'type': 'text', 'subtype': 'currency', 'required': True},
            {'name': 'Status', 'type': 'dropdown', 'options': ["Vacant", "Occupied"], 'required': True},
        ]
        pe.form_element(
            right_col,
            apartment_fields,
            name="Add Apartment",
            submit_text="Add",
            on_submit=self.add_apartment,
            small=True,
            field_per_row=2,
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

        apt_btn, open_apt_popup = pe.popup_card(
            right_col,
            button_text="Edit Apartments",
            title="Edit Apartments",
            small=False,
            button_size="full"
        )
        pe.style_secondary_button(apt_btn)

        def setup_apt_popup():
            content = open_apt_popup()

            header, location_dropdown = pe.create_popup_header_with_location(content)

            columns = [
                {'name': 'ID', 'key': 'apartment_ID', 'width': 80, 'editable': False},
                {'name': 'Location', 'key': 'city', 'width': 150, 'format': 'dropdown', 'options': location_options},
                {'name': 'Address', 'key': 'apartment_address', 'width': 150},
                {'name': 'Beds', 'key': 'number_of_beds', 'width': 80, "format": "number"},
                {'name': 'Monthly Rent', 'key': 'monthly_rent', 'width': 120, "format": "currency"},
                {'name': 'Status', 'key': 'status', 'width': 100, "format": "dropdown", 'options': ["Vacant", "Occupied"]}
            ]

            def get_data():
                try:
                    loc = location_dropdown.get()
                    return apartment_repo.get_all_apartments(location=loc)
                except Exception as e:
                    print(f"Error loading apartments: {e}")
                    return []

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

            pe.create_refresh_button(header, refresh_table)

            def refresh_with_reset():
                if hasattr(refresh_table, "reset_page"):
                    refresh_table.reset_page()
                refresh_table()
            
            refresh_timer, schedule_refresh = pe.create_debounced_refresh(content, refresh_with_reset)
            location_dropdown.configure(command=schedule_refresh)

        apt_btn.configure(command=setup_apt_popup)
# ============================= ^ Homepage UI Content ^ =====================================
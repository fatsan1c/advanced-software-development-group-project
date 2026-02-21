import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.user_repository as user_repo
import database_operations.repos.location_repository as location_repo
import database_operations.repos.apartment_repository as apartment_repo
from models.user import User
from datetime import datetime

try:
    from tkcalendar import Calendar
except Exception:
    Calendar = None

PRIMARY_BLUE = "#2F7FD8"
PRIMARY_BLUE_HOVER = "#2569B3"
ROUND_BOX = 16
ROUND_BTN = 14
ROUND_INPUT = 12


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

        occupancy_badge = ctk.CTkLabel(
            info_row,
            text="Total units: 0",
            font=("Arial", 12, "bold"),
            text_color=("#6E4B00", "#F5D27A"),
            fg_color=("#F4D28A", "#4B360D"),
            corner_radius=ROUND_INPUT,
            padx=10,
            pady=6,
        )
        occupancy_badge.pack(side="left", padx=6)

        location_wrap = ctk.CTkFrame(info_row, fg_color="transparent")
        location_wrap.pack(side="left", padx=(12, 0))

        ctk.CTkLabel(
            location_wrap,
            text="Location",
            font=("Arial", 13, "bold"),
            text_color=("gray35", "gray75"),
        ).pack(side="left", padx=(0, 10))

        cities = ["All Locations"] + location_repo.get_all_cities()
        location_dropdown = ctk.CTkComboBox(location_wrap, values=cities, width=240, font=("Arial", 13))
        location_dropdown.set("All Locations")
        location_dropdown.pack(side="left")

        # Stat grid - match Performance Reports layout
        stats = ctk.CTkFrame(occupancy_card, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 4))

        def stat_card(parent, title: str):
            card = ctk.CTkFrame(
                parent,
                corner_radius=ROUND_BOX,
                fg_color=("gray92", "gray17"),
                border_width=1,
                border_color=("gray80", "gray28"),
            )
            card.pack(side="left", expand=True, fill="both", padx=6, ipadx=8, ipady=10)

            ctk.CTkLabel(
                card,
                text=title.upper(),
                font=("Arial", 11, "bold"),
                text_color=("gray45", "gray70"),
                anchor="w",
            ).pack(fill="x", padx=12, pady=(8, 0))

            value = ctk.CTkLabel(
                card,
                text="0",
                font=("Arial", 20, "bold"),
                text_color=("#3B8ED0", "#3B8ED0"),
                anchor="w",
            )
            value.pack(fill="x", padx=12, pady=(2, 8))
            return value

        occupied_value = stat_card(stats, "Occupied")
        available_value = stat_card(stats, "Available")
        total_value = stat_card(stats, "Total")

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
        refresh_timer = {"id": None}
        def schedule_refresh(_choice=None):
            if refresh_timer["id"] is not None:
                try:
                    occupancy_card.after_cancel(refresh_timer["id"])
                except Exception:
                    pass
            refresh_timer["id"] = occupancy_card.after(150, update_occupancy_display)

        location_dropdown.configure(command=schedule_refresh)

        # Graph popup button - styled like finance
        button, open_popup_func = pe.popup_card(
            occupancy_card,
            title="Apartment Occupancy Graph",
            button_text="View Graphs",
            small=False,
            button_size="medium"
        )
        try:
            button.configure(
                height=40,
                font=("Arial", 14, "bold"),
                corner_radius=ROUND_BTN,
                fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
                hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
            )
            button.pack_configure(fill="x", padx=6, pady=(2, 0))
        except Exception:
            pass

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

            ctk.CTkLabel(row_dates, text="Start (DD/MM/YYYY):", font=("Arial", 13, "bold")).pack(side="left", padx=(0, 8))
            start_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            start_wrap.pack(side="left")
            start_entry = ctk.CTkEntry(start_wrap, width=140, font=("Arial", 13))
            if default_start:
                start_entry.insert(0, default_start)
            start_entry.pack(side="left")
            ctk.CTkLabel(row_dates, text="End (DD/MM/YYYY):", font=("Arial", 13, "bold")).pack(side="left", padx=(18, 8))
            end_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            end_wrap.pack(side="left")
            end_entry = ctk.CTkEntry(end_wrap, width=140, font=("Arial", 13))
            if default_end:
                end_entry.insert(0, default_end)
            end_entry.pack(side="left")

            def parse_ui_date(v):
                s = (v or "").strip()
                if not s:
                    return None
                try:
                    return datetime.strptime(s, "%d/%m/%Y").date()
                except Exception:
                    return None

            def open_calendar_for(entry_widget):
                popup = ctk.CTkToplevel(content.winfo_toplevel())
                popup.title("Select Date")
                popup.geometry("360x430")
                popup.resizable(False, False)
                popup.transient(content.winfo_toplevel())
                popup.grab_set()
                selected = parse_ui_date(entry_widget.get()) or datetime.now().date()
                mode = str(ctk.get_appearance_mode()).lower()
                is_dark = mode == "dark"
                shell = ctk.CTkFrame(popup, corner_radius=12, fg_color=("#F3F4F6", "#1F232A"),
                                     border_width=1, border_color=("#D8DCE2", "#2C313A"))
                shell.pack(fill="both", expand=True, padx=8, pady=8)
                ctk.CTkLabel(shell, text="Pick a Date", font=("Arial", 24, "bold"),
                             text_color=("#22252B", "#E9ECF2")).pack(anchor="w", padx=12, pady=(12, 4))
                ctk.CTkLabel(shell, text="Format: DD/MM/YYYY", font=("Arial", 12),
                             text_color=("#5E6672", "#AAB2BE")).pack(anchor="w", padx=12, pady=(0, 8))
                if Calendar is None:
                    ctk.CTkLabel(shell, text="Calendar unavailable.\nInstall tkcalendar package.",
                                 justify="center", font=("Arial", 12)).pack(pady=18)
                    ctk.CTkButton(shell, text="Close", command=popup.destroy, width=120).pack(pady=(10, 0))
                    return
                cal_kwargs = {"selectmode": "day", "date_pattern": "dd/mm/yyyy",
                             "year": selected.year, "month": selected.month, "day": selected.day}
                cal_kwargs.update({"font": ("Arial", 17), "headersfont": ("Arial", 15, "bold"),
                    "background": "#2A2F36" if is_dark else "#FFFFFF", "foreground": "#E9ECF2" if is_dark else "#1B2430",
                    "selectbackground": "#2F7FD8", "selectforeground": "#FFFFFF"})
                cal = Calendar(shell, **cal_kwargs, showweeknumbers=False)
                cal.pack(fill="both", expand=True, padx=12, pady=(4, 10))
                def apply_date():
                    entry_widget.delete(0, "end")
                    entry_widget.insert(0, cal.get_date())
                    popup.destroy()
                btn_row = ctk.CTkFrame(shell, fg_color="transparent")
                btn_row.pack(fill="x", padx=10, pady=(0, 10))
                ctk.CTkButton(btn_row, text="Cancel", command=popup.destroy, width=104, height=34, font=("Arial", 14),
                             fg_color=("gray80", "gray28"), hover_color=("gray70", "gray33")).pack(side="left")
                ctk.CTkButton(btn_row, text="Use Date", command=apply_date, width=104, height=34, font=("Arial", 14),
                             fg_color=(PRIMARY_BLUE, PRIMARY_BLUE), hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER)).pack(side="right")

            ctk.CTkButton(start_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                         command=lambda: open_calendar_for(start_entry),
                         fg_color=("gray80", "gray25"), hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))
            ctk.CTkButton(end_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                         command=lambda: open_calendar_for(end_entry),
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
            refresh_timer = {"id": None}
            def schedule_refresh(_=None):
                if refresh_timer["id"]:
                    try:
                        content.after_cancel(refresh_timer["id"])
                    except Exception:
                        pass
                refresh_timer["id"] = content.after(150, render_graph)
            popup_location_dropdown.configure(command=schedule_refresh)
            def on_grouping_change(choice=None):
                apply_grouping_defaults(grouping_dropdown.get())
                schedule_refresh(choice)
            grouping_dropdown.configure(command=on_grouping_change)
            render_graph()

        button.configure(command=setup_graph_popup)

    def load_account_content(self, row):
        accounts_card = pe.function_card(row, "Manage Accounts", side="left", pady=6, padx=8)

        fields = [
            {'name': 'Username', 'type': 'text', 'required': True},
            {'name': 'Role', 'type': 'dropdown', 'options': ['Admin', 'Manager', 'Finance Manager', 'Frontdesk', 'Maintenance'], 'required': True},
            {'name': 'Password', 'type': 'text', 'required': True},
            {'name': 'Location', 'type': 'dropdown', 'options': ['None'] + location_repo.get_all_cities(), 'required': False}
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
        try:
            button.configure(
                height=40,
                font=("Arial", 13, "bold"),
                corner_radius=ROUND_BTN,
                fg_color=("gray85", "gray25"),
                hover_color=("gray80", "gray30"),
                text_color=("gray15", "gray92"),
            )
            button.pack_configure(pady=(4, 0))
        except Exception:
            pass

        def setup_popup():
            content = open_popup_func()

            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            columns = [
                {'name': 'ID', 'key': 'user_ID', 'width': 80, 'editable': False},
                {'name': 'Username', 'key': 'username', 'width': 200},
                {'name': 'Location', 'key': 'city', 'width': 200},
                {'name': 'Role', 'key': 'role', 'width': 150}
            ]

            def get_data():
                return user_repo.get_all_users()

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

            ctk.CTkButton(
                header,
                text="⟳ Refresh",
                command=refresh_table,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25")
            ).pack(side="left")

        button.configure(command=setup_popup)

    def load_report_content(self, row, side="left"):
        reports_card = pe.function_card(row, "Performance Reports", side=side, pady=6, padx=8)

        # Top info row: vacant badge (left) + location selector (right) - match finance layout
        info_row = ctk.CTkFrame(reports_card, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 6))

        vacant_badge = ctk.CTkLabel(
            info_row,
            text="Vacant units: 0",
            font=("Arial", 12, "bold"),
            text_color=("#6E4B00", "#F5D27A"),
            fg_color=("#F4D28A", "#4B360D"),
            corner_radius=ROUND_INPUT,
            padx=10,
            pady=6,
        )
        vacant_badge.pack(side="left", padx=6)

        location_wrap = ctk.CTkFrame(info_row, fg_color="transparent")
        location_wrap.pack(side="left", padx=(12, 0))

        ctk.CTkLabel(
            location_wrap,
            text="Location",
            font=("Arial", 13, "bold"),
            text_color=("gray35", "gray75"),
        ).pack(side="left", padx=(0, 10))

        cities = ["All Locations"] + location_repo.get_all_cities()
        location_dropdown = ctk.CTkComboBox(location_wrap, values=cities, width=240, font=("Arial", 13))
        location_dropdown.set("All Locations")
        location_dropdown.pack(side="left")

        # Stat grid - match finance dashboard (Invoiced, Collected, Outstanding)
        stats = ctk.CTkFrame(reports_card, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 4))

        def stat_card(parent, title: str):
            card = ctk.CTkFrame(
                parent,
                corner_radius=ROUND_BOX,
                fg_color=("gray92", "gray17"),
                border_width=1,
                border_color=("gray80", "gray28"),
            )
            card.pack(side="left", expand=True, fill="both", padx=6, ipadx=8, ipady=10)

            ctk.CTkLabel(
                card,
                text=title.upper(),
                font=("Arial", 11, "bold"),
                text_color=("gray45", "gray70"),
                anchor="w",
            ).pack(fill="x", padx=12, pady=(8, 0))

            value = ctk.CTkLabel(
                card,
                text="£0.00",
                font=("Arial", 20, "bold"),
                text_color=("#3B8ED0", "#3B8ED0"),
                anchor="w",
            )
            value.pack(fill="x", padx=12, pady=(2, 8))
            return value

        actual_value = stat_card(stats, "Actual Revenue")
        lost_value = stat_card(stats, "Lost Revenue")
        potential_value = stat_card(stats, "Potential Revenue")

        def update_performance_display(choice=None):
            location = "all" if location_dropdown.get() == "All Locations" else location_dropdown.get()
            actual_revenue = apartment_repo.get_monthly_revenue(location)
            potential_revenue = apartment_repo.get_potential_revenue(location)
            lost_revenue = potential_revenue - actual_revenue
            total = apartment_repo.get_total_apartments(location)
            occupied = apartment_repo.get_all_occupancy(location)
            vacant = total - occupied

            actual_value.configure(text=f"£{actual_revenue:,.2f}")
            lost_value.configure(text=f"£{lost_revenue:,.2f}")
            potential_value.configure(text=f"£{potential_revenue:,.2f}")
            vacant_badge.configure(text=f"Vacant units: {vacant}")

        update_performance_display()
        refresh_timer = {"id": None}
        def schedule_refresh(_choice=None):
            if refresh_timer["id"] is not None:
                try:
                    reports_card.after_cancel(refresh_timer["id"])
                except Exception:
                    pass
            refresh_timer["id"] = reports_card.after(150, update_performance_display)

        location_dropdown.configure(command=schedule_refresh)

        button, open_popup_func = pe.popup_card(
            reports_card,
            title="Performance Report Graph",
            button_text="View Graphs",
            small=False,
            button_size="medium"
        )
        try:
            button.configure(
                height=40,
                font=("Arial", 14, "bold"),
                corner_radius=ROUND_BTN,
                fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
                hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
            )
            button.pack_configure(fill="x", padx=6, pady=(2, 0))
        except Exception:
            pass

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

            ctk.CTkLabel(row_dates, text="Start (DD/MM/YYYY):", font=("Arial", 13, "bold")).pack(side="left", padx=(0, 8))
            start_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            start_wrap.pack(side="left")
            start_entry = ctk.CTkEntry(start_wrap, width=140, font=("Arial", 13))
            if default_start:
                start_entry.insert(0, default_start)
            start_entry.pack(side="left")
            ctk.CTkLabel(row_dates, text="End (DD/MM/YYYY):", font=("Arial", 13, "bold")).pack(side="left", padx=(18, 8))
            end_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
            end_wrap.pack(side="left")
            end_entry = ctk.CTkEntry(end_wrap, width=140, font=("Arial", 13))
            if default_end:
                end_entry.insert(0, default_end)
            end_entry.pack(side="left")

            def parse_d(v):
                s = (v or "").strip()
                if not s:
                    return None
                try:
                    return datetime.strptime(s, "%d/%m/%Y").date()
                except Exception:
                    return None

            def open_cal(entry_widget):
                popup = ctk.CTkToplevel(content.winfo_toplevel())
                popup.title("Select Date")
                popup.geometry("360x430")
                popup.resizable(False, False)
                popup.transient(content.winfo_toplevel())
                popup.grab_set()
                selected = parse_d(entry_widget.get()) or datetime.now().date()
                is_dark = str(ctk.get_appearance_mode()).lower() == "dark"
                shell = ctk.CTkFrame(popup, corner_radius=12, fg_color=("#F3F4F6", "#1F232A"),
                                     border_width=1, border_color=("#D8DCE2", "#2C313A"))
                shell.pack(fill="both", expand=True, padx=8, pady=8)
                ctk.CTkLabel(shell, text="Pick a Date", font=("Arial", 24, "bold"),
                             text_color=("#22252B", "#E9ECF2")).pack(anchor="w", padx=12, pady=(12, 4))
                ctk.CTkLabel(shell, text="Format: DD/MM/YYYY", font=("Arial", 12),
                             text_color=("#5E6672", "#AAB2BE")).pack(anchor="w", padx=12, pady=(0, 8))
                if Calendar is None:
                    ctk.CTkLabel(shell, text="Calendar unavailable.\nInstall tkcalendar package.",
                                 justify="center", font=("Arial", 12)).pack(pady=18)
                    ctk.CTkButton(shell, text="Close", command=popup.destroy, width=120).pack(pady=(10, 0))
                    return
                cal_kwargs = {"selectmode": "day", "date_pattern": "dd/mm/yyyy",
                              "year": selected.year, "month": selected.month, "day": selected.day,
                              "font": ("Arial", 17), "headersfont": ("Arial", 15, "bold"),
                              "background": "#2A2F36" if is_dark else "#FFFFFF",
                              "foreground": "#E9ECF2" if is_dark else "#1B2430",
                              "selectbackground": "#2F7FD8", "selectforeground": "#FFFFFF"}
                cal = Calendar(shell, **cal_kwargs, showweeknumbers=False)
                cal.pack(fill="both", expand=True, padx=12, pady=(4, 10))
                def apply_date():
                    entry_widget.delete(0, "end")
                    entry_widget.insert(0, cal.get_date())
                    popup.destroy()
                btn_row = ctk.CTkFrame(shell, fg_color="transparent")
                btn_row.pack(fill="x", padx=10, pady=(0, 10))
                ctk.CTkButton(btn_row, text="Cancel", command=popup.destroy, width=104, height=34, font=("Arial", 14),
                             fg_color=("gray80", "gray28"), hover_color=("gray70", "gray33")).pack(side="left")
                ctk.CTkButton(btn_row, text="Use Date", command=apply_date, width=104, height=34, font=("Arial", 14),
                             fg_color=(PRIMARY_BLUE, PRIMARY_BLUE), hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER)).pack(side="right")

            ctk.CTkButton(start_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                         command=lambda: open_cal(start_entry), fg_color=("gray80", "gray25"),
                         hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))
            ctk.CTkButton(end_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                         command=lambda: open_cal(end_entry), fg_color=("gray80", "gray25"),
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
            refresh_timer = {"id": None}
            def schedule_refresh(_=None):
                if refresh_timer["id"]:
                    try:
                        content.after_cancel(refresh_timer["id"])
                    except Exception:
                        pass
                refresh_timer["id"] = content.after(150, render_graph)
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
        try:
            loc_btn.configure(
                height=40,
                font=("Arial", 13, "bold"),
                corner_radius=ROUND_BTN,
                fg_color=("gray85", "gray25"),
                hover_color=("gray80", "gray30"),
                text_color=("gray15", "gray92"),
            )
            loc_btn.pack_configure(pady=(4, 0))
        except Exception:
            pass

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
                return location_repo.get_all_locations()

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

            ctk.CTkButton(
                header,
                text="⟳ Refresh",
                command=refresh_table,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25")
            ).pack(side="left")

        loc_btn.configure(command=setup_loc_popup)

        # Right column: Add Apartment + Edit Apartments
        apartment_fields = [
            {'name': 'Location', 'type': 'dropdown', 'options': location_repo.get_all_cities(), 'required': True},
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
        try:
            apt_btn.configure(
                height=40,
                font=("Arial", 13, "bold"),
                corner_radius=ROUND_BTN,
                fg_color=("gray85", "gray25"),
                hover_color=("gray80", "gray30"),
                text_color=("gray15", "gray92"),
            )
            apt_btn.pack_configure(pady=(4, 0))
        except Exception:
            pass

        def setup_apt_popup():
            content = open_apt_popup()

            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

            cities = ["All Locations"] + location_repo.get_all_cities()
            location_dropdown = ctk.CTkComboBox(header, values=cities, width=220, font=("Arial", 13))
            location_dropdown.set("All Locations")
            location_dropdown.pack(side="left")

            columns = [
                {'name': 'ID', 'key': 'apartment_ID', 'width': 80, 'editable': False},
                {'name': 'Location', 'key': 'city', 'width': 150},
                {'name': 'Address', 'key': 'apartment_address', 'width': 150},
                {'name': 'Beds', 'key': 'number_of_beds', 'width': 80},
                {'name': 'Monthly Rent', 'key': 'monthly_rent', 'width': 120, "format": "currency"},
                {'name': 'Status', 'key': 'status', 'width': 100}
            ]

            def get_data():
                loc = location_dropdown.get()
                return apartment_repo.get_all_apartments(location=loc)

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

            ctk.CTkButton(
                header,
                text="⟳ Refresh",
                command=refresh_table,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25")
            ).pack(side="left", padx=(12, 0))

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

        apt_btn.configure(command=setup_apt_popup)
# ============================= ^ Homepage UI Content ^ =====================================
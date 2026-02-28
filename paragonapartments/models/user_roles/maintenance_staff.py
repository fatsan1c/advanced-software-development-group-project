import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.maintenance_repository as maintenance_repo
import database_operations.repos.location_repository as location_repo
from models.user import User


class MaintenanceStaff(User):
    """Maintenance staff with ability to view, manage, and resolve maintenance requests."""
    
    def __init__(self, username: str, location: str = None):
        super().__init__(username, role="Maintenance Staff", location=location)

    def _selected_location(self, dropdown_value: str | None) -> str:
        """Map UI dropdown value to repository location parameter."""
        if dropdown_value == "All Locations":
            return "all"
        return dropdown_value or "all"

# ============================= v Maintenance Staff functions v  =====================================
    
    def get_maintenance_stats(self, location: str = "all"):
        """Return maintenance statistics (used by the dashboard)."""
        return maintenance_repo.get_maintenance_stats(location)

    def create_maintenance_request(self, values):
        """Create a new maintenance request."""
        try:
            apartment_id = int(values.get("Apartment ID", 0))
            tenant_id = int(values.get("Tenant ID", 0))
            issue_description = values.get("Issue Description", "").strip()
            priority_level = int(values.get("Priority Level", 1))
            scheduled_date = values.get("Scheduled Date", "").strip() or None
            cost_estimate = values.get("Cost Estimate", "").strip()

            if not apartment_id:
                return "Apartment ID is required."
            if not tenant_id:
                return "Tenant ID is required."
            if not issue_description:
                return "Issue Description is required."
            if priority_level < 1 or priority_level > 5:
                return "Priority Level must be between 1 (low) and 5 (urgent)."

            cost = float(cost_estimate) if cost_estimate else None

            request_id = maintenance_repo.create_maintenance_request(
                apartment_id=apartment_id,
                tenant_id=tenant_id,
                issue_description=issue_description,
                priority_level=priority_level,
                scheduled_date=scheduled_date,
                cost=cost
            )
            return True if request_id else "Failed to create maintenance request."
        except Exception as e:
            return f"Failed to create request: {str(e)}"

    def update_maintenance_request_row(self, row_data, updated_data):
        """Update a maintenance request row from the editable table."""
        try:
            request_id = int(row_data.get("request_ID"))
            kwargs = {}

            if "priority_level" in updated_data:
                priority = int(updated_data["priority_level"])
                if priority < 1 or priority > 5:
                    return "Priority must be between 1 and 5."
                kwargs["priority_level"] = priority
            
            if "issue_description" in updated_data:
                kwargs["issue_description"] = updated_data["issue_description"]
            
            if "scheduled_date" in updated_data:
                kwargs["scheduled_date"] = updated_data["scheduled_date"] or None
            
            if "cost" in updated_data:
                cost_str = str(updated_data["cost"]).strip()
                kwargs["cost"] = float(cost_str) if cost_str else None
            
            if "completed" in updated_data:
                kwargs["completed"] = int(updated_data["completed"])

            success = maintenance_repo.update_maintenance_request(request_id, **kwargs)
            return True if success else "Update failed."
        except Exception as e:
            return f"Failed to update request: {str(e)}"

    def delete_maintenance_request_row(self, row_data):
        """Delete a maintenance request row from the table."""
        try:
            request_id = int(row_data.get("request_ID"))
            success = maintenance_repo.delete_maintenance_request(request_id)
            return True if success else "Delete failed."
        except Exception as e:
            return f"Failed to delete request: {str(e)}"

    def complete_maintenance_request(self, values):
        """Mark a maintenance request as completed and log the final cost."""
        try:
            request_id = int(values.get("Request ID", 0))
            final_cost = values.get("Final Cost", "").strip()

            if not request_id:
                return "Request ID is required."

            # Verify request exists and is not already completed
            request = maintenance_repo.get_maintenance_request_by_id(request_id)
            if not request:
                return f"Maintenance request ID {request_id} does not exist."
            if int(request.get("completed", 0)) == 1:
                return f"Request {request_id} is already marked as completed."

            cost = float(final_cost) if final_cost else None
            success = maintenance_repo.mark_maintenance_completed(request_id, cost)
            
            return True if success else "Failed to mark request as completed."
        except Exception as e:
            return f"Failed to complete request: {str(e)}"

    def schedule_maintenance(self, values):
        """Schedule a maintenance request by setting the scheduled date."""
        try:
            request_id = int(values.get("Request ID", 0))
            scheduled_date = values.get("Scheduled Date", "").strip()

            if not request_id:
                return "Request ID is required."
            if not scheduled_date:
                return "Scheduled Date is required (YYYY-MM-DD)."

            # Verify request exists
            request = maintenance_repo.get_maintenance_request_by_id(request_id)
            if not request:
                return f"Maintenance request ID {request_id} does not exist."
            if int(request.get("completed", 0)) == 1:
                return f"Cannot schedule completed request {request_id}."

            success = maintenance_repo.update_maintenance_request(
                request_id,
                scheduled_date=scheduled_date
            )
            
            return True if success else "Failed to schedule request."
        except Exception as e:
            return f"Failed to schedule request: {str(e)}"

# ============================= ^ Maintenance Staff functions ^ =====================================

# ============================= v Homepage UI Content v =====================================
    
    def load_homepage_content(self, home_page):
        """Load Maintenance Staff-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)

        container = pe.scrollable_container(parent=home_page)

        # Row 1: Dashboard Summary & Pending Requests
        row1 = pe.row_container(parent=container)
        self.load_summary_content(row1)
        self.load_pending_requests_content(row1)

        # Row 2: Complete Request & Schedule Request
        row2 = pe.row_container(parent=container)
        self.load_complete_request_content(row2)
        self.load_schedule_request_content(row2)

        # Row 3: Create Request
        row3 = pe.row_container(parent=container)
        self.load_create_request_content(row3)
        

    def load_summary_content(self, row):
        """Load maintenance statistics summary card."""
        summary_card = pe.function_card(row, "Maintenance Summary", side="left")

        # Top info row: high priority badge (left) + location selector (right)
        info_row = ctk.CTkFrame(summary_card, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 6))

        priority_badge = pe.info_badge(info_row, "High Priority: 0")

        location_dropdown = pe.location_dropdown_with_label(info_row)
        location_dropdown.set(self.location if self.location else "All Locations")

        # Stat grid - match Performance Reports layout
        stats = pe.stats_grid(summary_card)

        total_value = pe.stat_card(stats, "Total Requests", "0")
        pending_value = pe.stat_card(stats, "Pending", "0")
        completed_value = pe.stat_card(stats, "Completed", "0")
        cost_value = pe.stat_card(stats, "Avg Cost", "£0.00")

        def update_summary(choice=None):
            try:
                location = self._selected_location(location_dropdown.get())
                stats_data = self.get_maintenance_stats(location)
                
                total = stats_data.get('total_requests', 0) or 0
                pending = stats_data.get('pending_requests', 0) or 0
                completed = stats_data.get('completed_requests', 0) or 0
                high_priority = stats_data.get('high_priority_pending', 0) or 0
                avg_cost = stats_data.get('avg_cost', 0) or 0
                
                total_value.configure(text=str(total))
                pending_value.configure(text=str(pending))
                completed_value.configure(text=str(completed))
                cost_value.configure(text=f"£{avg_cost:.2f}")
                priority_badge.configure(text=f"High Priority: {high_priority}")
            except Exception as e:
                print(f"Error loading maintenance stats: {e}")

        update_summary()
        refresh_timer, schedule_refresh = pe.create_debounced_refresh(summary_card, update_summary)
        location_dropdown.configure(command=schedule_refresh)

    def load_pending_requests_content(self, row):
        """Load pending maintenance requests card with priority filtering."""
        pending_card = pe.function_card(row, "View Requests", side="left")

        button, open_popup = pe.popup_card(
            pending_card,
            title="Pending Maintenance Requests",
            button_text="View Pending Requests",
            small=False,
            button_size="medium"
        )
        pe.style_accent_secondary_button(button)
        button.pack(pady=(0, 14))

        def setup_popup():
            content = open_popup()

            # Filter controls
            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

            try:
                cities = ["All Locations"] + location_repo.get_all_cities()
            except Exception as e:
                print(f"Error loading cities: {e}")
                cities = ["All Locations"]
                
            location_dropdown = ctk.CTkComboBox(header, values=cities, width=180, font=("Arial", 13))
            location_dropdown.set(self.location if self.location else "All Locations")
            location_dropdown.pack(side="left", padx=(0, 15))

            ctk.CTkLabel(header, text="Priority:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))
            
            priority_dropdown = ctk.CTkComboBox(
                header, 
                values=["All", "1 - Low", "2", "3 - Medium", "4", "5 - Urgent"], 
                width=140, 
                font=("Arial", 13)
            )
            priority_dropdown.set("All")
            priority_dropdown.pack(side="left")

            columns = [
                {"name": "ID", "key": "request_ID", "width": 40, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 140, "editable": False},
                {"name": "Apartment", "key": "apartment_address", "width": 100, "editable": False},
                {"name": "City", "key": "city", "width": 70, "editable": False},
                {"name": "Issue", "key": "issue_description", "width": 250},
                {"name": "Priority", "key": "priority_level", "width": 65, "format": "dropdown", "options": [1, 2, 3, 4, 5]},
                {"name": "Reported", "key": "reported_date", "width": 80, "editable": False, "format": "date"},
                {"name": "Scheduled", "key": "scheduled_date", "width": 80, "format": "date"},
            ]

            def get_data():
                try:
                    location = self._selected_location(location_dropdown.get())
                    priority_val = priority_dropdown.get()
                    priority = None
                    if priority_val != "All":
                        priority = int(priority_val.split(" ")[0])
                    return maintenance_repo.get_maintenance_requests(location, completed=0, priority=priority)
                except Exception as e:
                    print(f"Error loading pending requests: {e}")
                    return []

            _, refresh_table = pe.data_table(
                content,
                columns,
                editable=False,
                deletable=False,
                refresh_data=get_data,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10,
                scrollable=False
            )

            # Refresh button
            ctk.CTkButton(
                header,
                text="⟳ Refresh",
                command=refresh_table,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25")
            ).pack(side="left", padx=(12, 0))

            # Auto-refresh on filter change
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
            priority_dropdown.configure(command=schedule_refresh)

        button.configure(command=setup_popup)

        self.load_scheduled_maintenance_button(pending_card)

        self.load_all_requests_button(pending_card)

    def load_complete_request_content(self, row):
        """Load complete maintenance request card with dropdown."""
        complete_card = pe.function_card(row, "Complete Request", side="left")

        # Define data fetcher and formatter for request dropdown
        def fetch_requests():
            return maintenance_repo.get_maintenance_requests(
                location=self.location if self.location else "all",
                completed=0
            )

        def format_request(req):
            issue_short = req['issue_description'][:40] + "..." if len(req['issue_description']) > 40 else req['issue_description']
            display = f"ID {req['request_ID']}: {issue_short} - {req['tenant_name']} (P{req['priority_level']})"
            return (display, req['request_ID'])

        # Create dynamic dropdown with refresh functionality
        request_dropdown, request_map, refresh_requests = pe.create_dynamic_dropdown_with_refresh(
            complete_card,
            "Select Request:",
            fetch_requests,
            format_request,
            "No pending requests"
        )

        # Form submission handler
        def handle_submit(values):
            selected = request_dropdown.get()
            if not selected or selected not in request_map:
                return "Please select a request"

            request_id = request_map[selected]
            
            submit_values = {
                "Request ID": request_id,
                "Final Cost": values.get("Final Cost", "")
            }

            result = self.complete_maintenance_request(submit_values)
            
            if result is True:
                refresh_requests()
                return True
            else:
                return result

        # Use styled form for Final Cost input
        fields = [
            {
                'name': 'Final Cost',
                'type': 'text',
                'subtype': 'currency',
                'required': False
            }
        ]

        pe.form_element(
            complete_card,
            fields,
            name="",
            submit_text="Mark Complete",
            on_submit=handle_submit,
            field_per_row=1
        )

    def load_schedule_request_content(self, row):
        """Load schedule maintenance request card with dropdown."""
        schedule_card = pe.function_card(row, "Schedule Request", side="left")

        # Define data fetcher and formatter for request dropdown
        def fetch_requests():
            return maintenance_repo.get_maintenance_requests(
                location=self.location if self.location else "all",
                completed=0
            )

        def format_request(req):
            issue_short = req['issue_description'][:30] + "..." if len(req['issue_description']) > 30 else req['issue_description']
            scheduled_status = f"[Scheduled: {req['scheduled_date']}]" if req['scheduled_date'] else "[Not Scheduled]"
            display = f"ID {req['request_ID']}: {issue_short} - {req['tenant_name']} (P{req['priority_level']}) {scheduled_status}"
            return (display, req['request_ID'])

        # Create dynamic dropdown with refresh functionality
        request_dropdown, request_map, refresh_requests = pe.create_dynamic_dropdown_with_refresh(
            schedule_card,
            "Select Request:",
            fetch_requests,
            format_request,
            "No pending requests"
        )

        # Form submission handler
        def handle_submit(values):
            selected = request_dropdown.get()
            if not selected or selected not in request_map:
                return "Please select a request"

            request_id = request_map[selected]
            
            submit_values = {
                "Request ID": request_id,
                "Scheduled Date": values.get("Scheduled Date", "")
            }

            result = self.schedule_maintenance(submit_values)
            
            if result is True:
                refresh_requests()
                return True
            else:
                return result

        # Use styled form for Scheduled Date input
        fields = [
            {
                'name': 'Scheduled Date',
                'type': 'text',
                'subtype': 'date',
                'required': True
            }
        ]

        pe.form_element(
            schedule_card,
            fields,
            name="",
            submit_text="Schedule Request",
            on_submit=handle_submit,
            field_per_row=1
        )

    def load_create_request_content(self, row):
        """Load create new maintenance request card with apartment dropdown."""
        create_card = pe.function_card(row, "Create Request", side="left")

        # Container for dynamic dropdown and refresh button
        dropdown_container = ctk.CTkFrame(create_card, fg_color="transparent")
        dropdown_container.pack(fill="x", padx=10, pady=(10, 0))

        # Define data fetcher and formatter for apartment dropdown
        def fetch_apartments():
            return maintenance_repo.get_apartments_with_tenants(self.location)

        def format_apartment(apt):
            display = f"{apt['apartment_address']} - {apt['tenant_name']} ({apt['city']})"
            value = {
                'apartment_id': apt['apartment_ID'],
                'tenant_id': apt['tenant_ID']
            }
            return (display, value)

        # Create dynamic dropdown with refresh functionality (with custom refresh button position)
        # First create label
        ctk.CTkLabel(
            dropdown_container,
            text="Select Apartment:",
            font=("Arial", 13, "bold")
        ).pack(pady=(0, 5))

        # Create a horizontal container for dropdown and refresh button
        dropdown_row = ctk.CTkFrame(dropdown_container, fg_color="transparent")
        dropdown_row.pack(fill="x", pady=(0, 8))

        apartment_dropdown = ctk.CTkComboBox(
            dropdown_row,
            values=["Loading..."],
            font=("Arial", 12),
            state="readonly"
        )
        apartment_dropdown.pack(side="left", fill="x", expand=True)

        apartment_map = {}

        def refresh_apartments():
            apartments = fetch_apartments()
            
            if not apartments:
                apartment_dropdown.configure(values=["No apartments with active leases"])
                apartment_dropdown.set("No apartments with active leases")
                apartment_map.clear()
                return

            apartment_options = []
            apartment_map.clear()
            for apt in apartments:
                display, value = format_apartment(apt)
                apartment_options.append(display)
                apartment_map[display] = value

            apartment_dropdown.configure(values=apartment_options)
            apartment_dropdown.set(apartment_options[0])

        refresh_btn = pe.create_refresh_button(dropdown_row, refresh_apartments, side="left", padx=(10, 0))

        # Initial load
        refresh_apartments()

        # Form submission handler
        def handle_submit(values):
            selected_apt = apartment_dropdown.get()
            if not selected_apt or selected_apt not in apartment_map:
                return "Please select an apartment"

            apt_info = apartment_map[selected_apt]
            priority_str = values.get("Priority Level", "3 - Medium")
            
            # Extract priority number
            priority = int(priority_str.split(" ")[0])

            submit_values = {
                "Apartment ID": apt_info['apartment_id'],
                "Tenant ID": apt_info['tenant_id'],
                "Issue Description": values.get("Issue Description", ""),
                "Priority Level": priority,
                "Scheduled Date": values.get("Scheduled Date", ""),
                "Cost Estimate": values.get("Cost Estimate", "")
            }

            result = self.create_maintenance_request(submit_values)
            
            if result is True:
                refresh_apartments()
                return True
            else:
                return result

        # Use styled form for input fields
        fields = [
            {
                'name': 'Issue Description',
                'type': 'text',
                'required': True,
                # 'placeholder': 'Describe the maintenance issue'
            },
            {
                'name': 'Priority Level',
                'type': 'dropdown',
                'options': ["1 - Low", "2", "3 - Medium", "4", "5 - Urgent"],
                'default': "3 - Medium",
                'required': True
            },
            {
                'name': 'Cost Estimate',
                'type': 'text',
                'subtype': 'currency',
                'required': False,
                # 'placeholder': '£0.00'
            },
            {
                'name': 'Scheduled Date',
                'type': 'text',
                'subtype': 'date',
                'required': False,
                # 'placeholder': 'YYYY-MM-DD'
            }
        ]

        pe.form_element(
            create_card,
            fields,
            name="",
            submit_text="Create Request",
            on_submit=handle_submit,
            field_per_row=2
        )

    def load_scheduled_maintenance_button(self, parent):
        """Load upcoming scheduled maintenance card."""
        button, open_popup = pe.popup_card(
            parent,
            title="Upcoming Scheduled Maintenance",
            button_text="View Upcoming Schedule",
            button_size="medium"
        )
        pe.style_accent_secondary_button(button)
        button.pack(pady=(0, 10))

        def setup_popup():
            content = open_popup()

            # Filter controls
            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

            try:
                cities = ["All Locations"] + location_repo.get_all_cities()
            except Exception as e:
                print(f"Error loading cities: {e}")
                cities = ["All Locations"]
                
            location_dropdown = ctk.CTkComboBox(header, values=cities, width=220, font=("Arial", 13))
            location_dropdown.set(self.location if self.location else "All Locations")
            location_dropdown.pack(side="left")

            columns = [
                {"name": "ID", "key": "request_ID", "width": 40, "editable": False},
                {"name": "Scheduled", "key": "scheduled_date", "width": 80, "editable": False, "format": "date"},
                {"name": "Priority", "key": "priority_level", "width": 65, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 140, "editable": False},
                {"name": "Apartment", "key": "apartment_address", "width": 100, "editable": False},
                {"name": "City", "key": "city", "width": 70, "editable": False},
                {"name": "Issue", "key": "issue_description", "width": 250, "editable": False},
                {"name": "Est. Cost", "key": "cost", "width": 100, "format": "currency", "editable": False},
            ]

            def get_data():
                try:
                    location = self._selected_location(location_dropdown.get())
                    return maintenance_repo.get_scheduled_maintenance(location)
                except Exception as e:
                    print(f"Error loading scheduled maintenance: {e}")
                    return []

            _, refresh_table = pe.data_table(
                content,
                columns,
                editable=False,
                deletable=False,
                refresh_data=get_data,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10,
                scrollable=False
            )

            # Refresh button
            pe.create_refresh_button(header, refresh_table, side="left", padx=(12, 0))

            # Auto-refresh on location change
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

        button.configure(command=setup_popup)

    def load_all_requests_button(self, parent):
        """Load view/edit all maintenance requests card."""
        button, open_popup = pe.popup_card(
            parent,
            title="Maintenance Requests",
            button_text="View / Edit All Requests",
            small=False,
            button_size="medium"
        )
        pe.style_secondary_button(button)

        def setup_popup():
            content = open_popup()

            # Filter controls
            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(5, 10))

            ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

            try:
                cities = ["All Locations"] + location_repo.get_all_cities()
            except Exception as e:
                print(f"Error loading cities: {e}")
                cities = ["All Locations"]
                
            location_dropdown = ctk.CTkComboBox(header, values=cities, width=180, font=("Arial", 13))
            location_dropdown.set(self.location if self.location else "All Locations")
            location_dropdown.pack(side="left", padx=(0, 15))

            ctk.CTkLabel(header, text="Status:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))
            
            status_dropdown = ctk.CTkComboBox(
                header, 
                values=["All", "Pending", "Completed"], 
                width=140, 
                font=("Arial", 13)
            )
            status_dropdown.set("All")
            status_dropdown.pack(side="left")

            columns = [
                {"name": "ID", "key": "request_ID", "width": 20, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 90, "editable": False},
                {"name": "Apartment", "key": "apartment_address", "width": 90, "editable": False},
                {"name": "City", "key": "city", "width": 60, "editable": False},
                {"name": "Issue", "key": "issue_description", "width": 190},
                {"name": "Priority", "key": "priority_level", "width": 60, "format": "dropdown", "options": [1, 2, 3, 4, 5]},
                {"name": "Reported", "key": "reported_date", "width": 70, "editable": False, "format": "date"},
                {"name": "Scheduled", "key": "scheduled_date", "width": 80, "format": "date"},
                {"name": "Done", "key": "completed", "width": 45, "format": "boolean"},
                {"name": "Cost", "key": "cost", "width": 40, "format": "currency"},
            ]

            def get_data():
                try:
                    location = self._selected_location(location_dropdown.get())
                    status_val = status_dropdown.get()
                    completed = None
                    if status_val == "Pending":
                        completed = 0
                    elif status_val == "Completed":
                        completed = 1
                    return maintenance_repo.get_maintenance_requests(location, completed=completed)
                except Exception as e:
                    print(f"Error loading maintenance requests: {e}")
                    return []

            _, refresh_table = pe.data_table(
                content,
                columns,
                editable=True,
                deletable=True,
                refresh_data=get_data,
                on_delete=self.delete_maintenance_request_row,
                on_update=self.update_maintenance_request_row,
                show_refresh_button=False,
                render_batch_size=20,
                page_size=10,
                scrollable=False
            )

            # Refresh button
            pe.create_refresh_button(header, refresh_table, side="left", padx=(12, 0))

            # Auto-refresh on filter change
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
            status_dropdown.configure(command=schedule_refresh)

        button.configure(command=setup_popup)

# ============================= ^ Homepage UI Content ^ =====================================
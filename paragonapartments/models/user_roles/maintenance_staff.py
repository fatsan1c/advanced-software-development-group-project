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

        # Row 3: Create Request (left) & Scheduled Maintenance + Manage All Requests (right column)
        row3 = pe.row_container(parent=container)
        self.load_create_request_content(row3)
        
        # Right column container for scheduled and manage
        right_column = ctk.CTkFrame(row3, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.load_scheduled_maintenance_content(right_column)
        self.load_all_requests_content(right_column)

    def load_summary_content(self, row):
        """Load maintenance statistics summary card."""
        summary_card = pe.function_card(row, "Maintenance Dashboard", side="left")

        try:
            cities = ["All Locations"] + location_repo.get_all_cities()
        except Exception as e:
            print(f"Error loading cities: {e}")
            cities = ["All Locations"]
            
        location_dropdown = ctk.CTkComboBox(
            summary_card,
            values=cities,
            width=200,
            font=("Arial", 14)
        )
        location_dropdown.set(self.location if self.location else "All Locations")
        location_dropdown.pack(pady=10, padx=20)

        result_label = ctk.CTkLabel(
            summary_card,
            text="",
            font=("Arial", 15, "bold"),
            text_color="#3B8ED0"
        )
        result_label.pack(pady=10, padx=20)

        def update_summary():
            try:
                location = self._selected_location(location_dropdown.get())
                stats = self.get_maintenance_stats(location)
                
                total = stats.get('total_requests', 0) or 0
                pending = stats.get('pending_requests', 0) or 0
                completed = stats.get('completed_requests', 0) or 0
                high_priority = stats.get('high_priority_pending', 0) or 0
                avg_cost = stats.get('avg_cost', 0) or 0
                
                result_label.configure(
                    text=(
                        f"Total Requests: {total} | "
                        f"Pending: {pending} | "
                        f"Completed: {completed}\n"
                        f"High Priority Pending: {high_priority} | "
                        f"Avg Cost: £{avg_cost:.2f}"
                    )
                )
            except Exception as e:
                result_label.configure(text=f"Error loading stats: {str(e)}", text_color="red")

        # Auto-refresh summary on location change
        refresh_timer = {"id": None}
        def schedule_refresh(_choice=None):
            if refresh_timer["id"] is not None:
                try:
                    summary_card.after_cancel(refresh_timer["id"])
                except Exception:
                    pass
            refresh_timer["id"] = summary_card.after(150, update_summary)

        location_dropdown.configure(command=schedule_refresh)
        update_summary()

    def load_pending_requests_content(self, row):
        """Load pending maintenance requests card with priority filtering."""
        pending_card = pe.function_card(row, "Pending Requests", side="left")

        button, open_popup = pe.popup_card(
            pending_card,
            title="Pending Maintenance Requests",
            button_text="View Pending Requests",
            small=False,
            button_size="medium"
        )

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
                {"name": "ID", "key": "request_ID", "width": 70, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 160, "editable": False},
                {"name": "Apartment", "key": "apartment_address", "width": 120, "editable": False},
                {"name": "City", "key": "city", "width": 120, "editable": False},
                {"name": "Issue", "key": "issue_description", "width": 280},
                {"name": "Priority", "key": "priority_level", "width": 90, "format": "number"},
                {"name": "Reported", "key": "reported_date", "width": 110, "editable": False},
                {"name": "Scheduled", "key": "scheduled_date", "width": 110, "format": "date"},
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

    def load_complete_request_content(self, row):
        """Load complete maintenance request card with dropdown."""
        complete_card = pe.function_card(row, "Complete Request", side="left")

        # Form container
        form_container = ctk.CTkFrame(complete_card, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Request selection
        ctk.CTkLabel(
            form_container,
            text="Select Request:",
            font=("Arial", 13, "bold")
        ).pack(pady=(5, 2))

        request_dropdown = ctk.CTkComboBox(
            form_container,
            values=["Loading..."],
            width=400,
            font=("Arial", 11),
            state="readonly"
        )
        request_dropdown.pack(pady=(0, 5))

        # Refresh button
        def refresh_requests():
            pending_requests = maintenance_repo.get_maintenance_requests(
                location=self.location if self.location else "all",
                completed=0
            )

            if not pending_requests:
                request_dropdown.configure(values=["No pending requests"])
                request_dropdown.set("No pending requests")
                request_map.clear()
                return

            request_options = []
            request_map.clear()
            for req in pending_requests:
                issue_short = req['issue_description'][:40] + "..." if len(req['issue_description']) > 40 else req['issue_description']
                display = f"ID {req['request_ID']}: {issue_short} - {req['tenant_name']} (P{req['priority_level']})"
                request_options.append(display)
                request_map[display] = req['request_ID']

            request_dropdown.configure(values=request_options)
            request_dropdown.set(request_options[0])

        request_map = {}

        ctk.CTkButton(
            form_container,
            text="⟳ Refresh",
            command=refresh_requests,
            font=("Arial", 11),
            height=28,
            width=100,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray25")
        ).pack(pady=(0, 10))

        # Final Cost
        ctk.CTkLabel(
            form_container,
            text="Final Cost (Optional):",
            font=("Arial", 13, "bold")
        ).pack(pady=(5, 2))

        cost_entry = ctk.CTkEntry(
            form_container,
            width=200,
            font=("Arial", 12),
            placeholder_text="£0.00"
        )
        cost_entry.pack(pady=(0, 10))

        # Status label
        status_label = ctk.CTkLabel(
            form_container,
            text="",
            font=("Arial", 12)
        )
        status_label.pack(pady=(5, 0))

        # Submit button
        def submit_form():
            selected = request_dropdown.get()
            if not selected or selected not in request_map:
                status_label.configure(text="Please select a request", text_color="red")
                return

            request_id = request_map[selected]
            cost = cost_entry.get().strip()

            values = {
                "Request ID": request_id,
                "Final Cost": cost
            }

            result = self.complete_maintenance_request(values)
            
            if result is True:
                status_label.configure(text="✓ Request marked as completed!", text_color="green")
                cost_entry.delete(0, 'end')
                refresh_requests()
            else:
                status_label.configure(text=f"✗ {result}", text_color="red")

        ctk.CTkButton(
            form_container,
            text="Mark Complete",
            command=submit_form,
            font=("Arial", 13, "bold"),
            height=35,
            width=200
        ).pack(pady=(10, 5))

        # Initial load
        refresh_requests()

    def load_schedule_request_content(self, row):
        """Load schedule maintenance request card with dropdown."""
        schedule_card = pe.function_card(row, "Schedule Request", side="left")

        # Form container
        form_container = ctk.CTkFrame(schedule_card, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Request selection
        ctk.CTkLabel(
            form_container,
            text="Select Request:",
            font=("Arial", 13, "bold")
        ).pack(pady=(5, 2))

        request_dropdown = ctk.CTkComboBox(
            form_container,
            values=["Loading..."],
            width=450,
            font=("Arial", 11),
            state="readonly"
        )
        request_dropdown.pack(pady=(0, 5))

        # Refresh button
        def refresh_requests():
            all_pending = maintenance_repo.get_maintenance_requests(
                location=self.location if self.location else "all",
                completed=0
            )

            if not all_pending:
                request_dropdown.configure(values=["No pending requests"])
                request_dropdown.set("No pending requests")
                request_map.clear()
                return

            request_options = []
            request_map.clear()
            for req in all_pending:
                issue_short = req['issue_description'][:30] + "..." if len(req['issue_description']) > 30 else req['issue_description']
                scheduled_status = f"[Scheduled: {req['scheduled_date']}]" if req['scheduled_date'] else "[Not Scheduled]"
                display = f"ID {req['request_ID']}: {issue_short} - {req['tenant_name']} (P{req['priority_level']}) {scheduled_status}"
                request_options.append(display)
                request_map[display] = req['request_ID']

            request_dropdown.configure(values=request_options)
            request_dropdown.set(request_options[0])

        request_map = {}

        ctk.CTkButton(
            form_container,
            text="⟳ Refresh",
            command=refresh_requests,
            font=("Arial", 11),
            height=28,
            width=100,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray25")
        ).pack(pady=(0, 10))

        # Scheduled Date
        ctk.CTkLabel(
            form_container,
            text="Scheduled Date:",
            font=("Arial", 13, "bold")
        ).pack(pady=(5, 2))

        date_entry = ctk.CTkEntry(
            form_container,
            width=200,
            font=("Arial", 12),
            placeholder_text="YYYY-MM-DD"
        )
        date_entry.pack(pady=(0, 10))

        # Status label
        status_label = ctk.CTkLabel(
            form_container,
            text="",
            font=("Arial", 12)
        )
        status_label.pack(pady=(5, 0))

        # Submit button
        def submit_form():
            selected = request_dropdown.get()
            if not selected or selected not in request_map:
                status_label.configure(text="Please select a request", text_color="red")
                return

            request_id = request_map[selected]
            scheduled_date = date_entry.get().strip()

            values = {
                "Request ID": request_id,
                "Scheduled Date": scheduled_date
            }

            result = self.schedule_maintenance(values)
            
            if result is True:
                status_label.configure(text="✓ Request scheduled successfully!", text_color="green")
                date_entry.delete(0, 'end')
                refresh_requests()
            else:
                status_label.configure(text=f"✗ {result}", text_color="red")

        ctk.CTkButton(
            form_container,
            text="Schedule Request",
            command=submit_form,
            font=("Arial", 13, "bold"),
            height=35,
            width=200
        ).pack(pady=(10, 5))

        # Initial load
        refresh_requests()

    def load_create_request_content(self, row):
        """Load create new maintenance request card with apartment dropdown."""
        create_card = pe.function_card(row, "Create Request", side="left")

        # Form container
        form_container = ctk.CTkFrame(create_card, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Apartment selection
        ctk.CTkLabel(
            form_container,
            text="Select Apartment:",
            font=("Arial", 13, "bold")
        ).pack(pady=(5, 2))

        apartment_dropdown = ctk.CTkComboBox(
            form_container,
            values=["Loading..."],
            width=400,
            font=("Arial", 12),
            state="readonly"
        )
        apartment_dropdown.pack(pady=(0, 5))

        # Refresh button
        def refresh_apartments():
            apartments = maintenance_repo.get_apartments_with_tenants(self.location)
            
            if not apartments:
                apartment_dropdown.configure(values=["No apartments with active leases"])
                apartment_dropdown.set("No apartments with active leases")
                apartment_map.clear()
                return

            apartment_options = []
            apartment_map.clear()
            for apt in apartments:
                display = f"{apt['apartment_address']} - {apt['tenant_name']} ({apt['city']})"
                apartment_options.append(display)
                apartment_map[display] = {
                    'apartment_id': apt['apartment_ID'],
                    'tenant_id': apt['tenant_ID']
                }

            apartment_dropdown.configure(values=apartment_options)
            apartment_dropdown.set(apartment_options[0])

        apartment_map = {}

        ctk.CTkButton(
            form_container,
            text="⟳ Refresh",
            command=refresh_apartments,
            font=("Arial", 11),
            height=28,
            width=100,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray25")
        ).pack(pady=(0, 10))

        # Issue Description
        ctk.CTkLabel(
            form_container,
            text="Issue Description:",
            font=("Arial", 13, "bold")
        ).pack(pady=(5, 2))

        issue_entry = ctk.CTkEntry(
            form_container,
            width=400,
            font=("Arial", 12),
            placeholder_text="Describe the maintenance issue"
        )
        issue_entry.pack(pady=(0, 10))

        # Priority Level
        ctk.CTkLabel(
            form_container,
            text="Priority Level:",
            font=("Arial", 13, "bold")
        ).pack(pady=(5, 2))

        priority_dropdown = ctk.CTkComboBox(
            form_container,
            values=["1 - Low", "2", "3 - Medium", "4", "5 - Urgent"],
            width=200,
            font=("Arial", 12),
            state="readonly"
        )
        priority_dropdown.set("3 - Medium")
        priority_dropdown.pack(pady=(0, 10))

        # Scheduled Date (optional)
        ctk.CTkLabel(
            form_container,
            text="Scheduled Date (Optional):",
            font=("Arial", 13, "bold")
        ).pack(pady=(5, 2))

        scheduled_entry = ctk.CTkEntry(
            form_container,
            width=200,
            font=("Arial", 12),
            placeholder_text="YYYY-MM-DD"
        )
        scheduled_entry.pack(pady=(0, 10))

        # Cost Estimate (optional)
        ctk.CTkLabel(
            form_container,
            text="Cost Estimate (Optional):",
            font=("Arial", 13, "bold")
        ).pack(pady=(5, 2))

        cost_entry = ctk.CTkEntry(
            form_container,
            width=200,
            font=("Arial", 12),
            placeholder_text="£0.00"
        )
        cost_entry.pack(pady=(0, 10))

        # Status label
        status_label = ctk.CTkLabel(
            form_container,
            text="",
            font=("Arial", 12)
        )
        status_label.pack(pady=(5, 0))

        # Submit button
        def submit_form():
            selected_apt = apartment_dropdown.get()
            if not selected_apt or selected_apt not in apartment_map:
                status_label.configure(text="Please select an apartment", text_color="red")
                return

            apt_info = apartment_map[selected_apt]
            issue = issue_entry.get().strip()
            priority_str = priority_dropdown.get()
            scheduled = scheduled_entry.get().strip()
            cost = cost_entry.get().strip()

            # Extract priority number
            priority = int(priority_str.split(" ")[0])

            values = {
                "Apartment ID": apt_info['apartment_id'],
                "Tenant ID": apt_info['tenant_id'],
                "Issue Description": issue,
                "Priority Level": priority,
                "Scheduled Date": scheduled,
                "Cost Estimate": cost
            }

            result = self.create_maintenance_request(values)
            
            if result is True:
                status_label.configure(text="✓ Request created successfully!", text_color="green")
                # Clear form
                issue_entry.delete(0, 'end')
                scheduled_entry.delete(0, 'end')
                cost_entry.delete(0, 'end')
                priority_dropdown.set("3 - Medium")
            else:
                status_label.configure(text=f"✗ {result}", text_color="red")

        ctk.CTkButton(
            form_container,
            text="Create Request",
            command=submit_form,
            font=("Arial", 13, "bold"),
            height=35,
            width=200
        ).pack(pady=(10, 5))

        # Initial load
        refresh_apartments()

    def load_scheduled_maintenance_content(self, row):
        """Load upcoming scheduled maintenance card."""
        scheduled_card = pe.function_card(row, "Scheduled Maintenance", side="top", pady=0, padx=0)

        button, open_popup = pe.popup_card(
            scheduled_card,
            title="Upcoming Scheduled Maintenance",
            button_text="View Schedule",
            small=False,
            button_size="medium"
        )

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
                {"name": "ID", "key": "request_ID", "width": 70, "editable": False},
                {"name": "Scheduled", "key": "scheduled_date", "width": 110, "editable": False},
                {"name": "Priority", "key": "priority_level", "width": 80, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 160, "editable": False},
                {"name": "Apartment", "key": "apartment_address", "width": 120, "editable": False},
                {"name": "City", "key": "city", "width": 120, "editable": False},
                {"name": "Issue", "key": "issue_description", "width": 300, "editable": False},
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
            ctk.CTkButton(
                header,
                text="⟳ Refresh",
                command=refresh_table,
                height=32,
                width=120,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray25")
            ).pack(side="left", padx=(12, 0))

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

    def load_all_requests_content(self, row):
        """Load view/edit all maintenance requests card."""
        all_requests_card = pe.function_card(row, "Manage All Requests", side="top", pady=0, padx=0)

        button, open_popup = pe.popup_card(
            all_requests_card,
            title="All Maintenance Requests",
            button_text="View / Edit All Requests",
            small=False,
            button_size="large"
        )

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
                {"name": "ID", "key": "request_ID", "width": 70, "editable": False},
                {"name": "Tenant", "key": "tenant_name", "width": 150, "editable": False},
                {"name": "Apartment", "key": "apartment_address", "width": 120, "editable": False},
                {"name": "City", "key": "city", "width": 110, "editable": False},
                {"name": "Issue", "key": "issue_description", "width": 260},
                {"name": "Priority", "key": "priority_level", "width": 80, "format": "number"},
                {"name": "Reported", "key": "reported_date", "width": 105, "editable": False},
                {"name": "Scheduled", "key": "scheduled_date", "width": 105, "format": "date"},
                {"name": "Done (0/1)", "key": "completed", "width": 95},
                {"name": "Cost", "key": "cost", "width": 100, "format": "currency"},
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
            status_dropdown.configure(command=schedule_refresh)

        button.configure(command=setup_popup)

# ============================= ^ Homepage UI Content ^ =====================================
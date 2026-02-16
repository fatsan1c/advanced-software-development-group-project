import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.tenants_repository as tenant_repo
import pages.components.input_validation as input_validation
from models.user import User


class FrontDeskStaff(User):
    """Front desk staff with tenant management and maintenance request handling."""
    
    def __init__(self, username: str, location: str = ""):
        super().__init__(username, role="Front Desk Staff", location=location)

# ============================= v Front Desk functions v  =====================================
    def register_tenant(self, values):
        """Register a new tenant with their details and create lease agreement."""
        from database_operations.repos import apartment_repository as apt_repo
        from database_operations.repos import location_repository as loc_repo
        
        first_name = values.get('First Name', '')
        last_name = values.get('Last Name', '')
        name = f"{first_name} {last_name}".strip()
        ni_number = values.get('NI Number', '')
        email = values.get('Email', '')
        phone = values.get('Phone', '')
        occupation = values.get('Occupation', '')
        references = values.get('References', '')
        
        city = values.get('City', '')
        apartment_full = values.get('Apartment', '')
        # Extract apartment address from formatted string (e.g., "Apartment 6 - 2 beds - £850/month")
        apartment = apartment_full.split(' - ')[0] if ' - ' in apartment_full else apartment_full
        start_date = values.get('Contract Start Date', '')
        end_date = values.get('Contract End Date', '')
        
        try:
            # Create tenant record
            tenant_repo.create_tenant(name, ni_number, email, phone, occupation, references)
            
            # Get the newly created tenant's ID
            tenant_id = tenant_repo.get_last_tenant_id()
            
            if tenant_id and apartment:
                # Get apartment_id from apartment address
                all_apartments = apt_repo.get_all_apartments()
                apartment_id = None
                monthly_rent = 0
                
                for apt in all_apartments:
                    if apt['apartment_address'] == apartment and apt['city'] == city:
                        apartment_id = apt['apartment_ID']
                        monthly_rent = apt['monthly_rent']
                        break
                
                if apartment_id:
                    # Create lease agreement
                    tenant_repo.create_lease_agreement(
                        tenant_id, apartment_id, start_date, end_date, monthly_rent
                    )
                    
                    # Update apartment occupied status
                    apt_repo.update_apartment(apartment_id, occupied=1)
            
            return True  # Success
        except Exception as e:
            return f"Failed to register tenant: {str(e)}"

    def get_tenant_info(self, tenant_id: int = None):
        """Retrieve information for a specific tenant from the user's location."""
        result = tenant_repo.get_tenant_by_id(tenant_id, location=self.location) if tenant_id else None
        if result:
            info = (
                f"Tenant ID: {result['tenant_ID']}\n"
                f"Name: {result['name']}\n"
                f"NI Number: {result['NI_number']}\n"
                f"Email: {result['email']}\n"
                f"Phone: {result['phone']}"
            )
            return info
        return "Tenant not found or not in your location"

    def register_maintenance_request(self, values):
        """Register a maintenance request for a tenant."""
        try:
            apartment_id = values.get('apartment_id')
            tenant_id = values.get('tenant_id')
            issue_description = values.get('issue_description')
            priority_level = values.get('priority_level', 2)
            reported_date = values.get('reported_date')
            
            tenant_repo.create_maintenance_request(
                apartment_id, tenant_id, issue_description, 
                priority_level, reported_date
            )
            return True
        except Exception as e:
            return f"Failed to register maintenance request: {str(e)}"

    def register_complaint(self, values):
        """Register a complaint from a tenant."""
        try:
            tenant_id = values.get('tenant_id')
            description = values.get('description')
            date_submitted = values.get('date_submitted')
            
            tenant_repo.create_complaint(tenant_id, description, date_submitted)
            return True
        except Exception as e:
            return f"Failed to register complaint: {str(e)}"
# ============================= ^ Front Desk functions ^ =====================================

# ============================= v Homepage UI Content v =====================================
    def load_homepage_content(self, home_page):
        """Load Front Desk Staff-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)
        
        # First row - Tenant Management
        row1 = pe.row_container(parent=home_page)
        self.load_tenant_content(row1)
        
        # Second row - Maintenance and Complaints
        row2 = pe.row_container(parent=home_page)
        self.load_maintenance_content(row2)
        self.load_complaints_content(row2)

    def load_tenant_content(self, row):
        from database_operations.repos import location_repository as loc_repo
        from database_operations.repos import apartment_repository as apt_repo
        
        tenant_card = pe.function_card(row, "Tenant Management", side="left")
        
        # Get available apartments for this location (vacant only)
        all_apartments = apt_repo.get_all_apartments()
        location_apartments_list = [apt for apt in all_apartments 
                              if apt['city'] == self.location and apt['status'] == 'Vacant']
        
        # Format apartment options with more details
        apartment_options = [
            f"{apt['apartment_address']} - {apt['number_of_beds']} beds - £{apt['monthly_rent']}/month" 
            for apt in location_apartments_list
        ]
        
        # Define fields for tenant registration
        fields = [
            {'name': 'First Name', 'type': 'text', 'required': True},
            {'name': 'Last Name', 'type': 'text', 'required': True},
            {'name': 'NI Number', 'type': 'text', 'placeholder': 'AB123456C', 'required': True},
            {'name': 'Email', 'type': 'text', 'placeholder': 'example@email.com', 'required': True},
            {'name': 'Phone', 'type': 'text', 'placeholder': '07123456789', 'required': True},
            {'name': 'Occupation', 'type': 'text', 'placeholder': 'Job title', 'required': True},
            {'name': 'References', 'type': 'text', 'placeholder': 'Previous landlord, employer, etc.', 'required': False},
            {'name': 'City', 'type': 'dropdown', 'options': [self.location], 'default': self.location, 'required': True},
            {'name': 'Apartment', 'type': 'dropdown', 'options': apartment_options if apartment_options else ['No vacant apartments'], 'required': True},
            {'name': 'Contract Start Date', 'type': 'text', 'placeholder': 'YYYY-MM-DD (e.g., 2026-03-01)', 'required': True},
            {'name': 'Contract End Date', 'type': 'text', 'placeholder': 'YYYY-MM-DD (e.g., 2027-03-01)', 'required': True}
        ]
        
        # Create tenant registration form
        pe.form_element(tenant_card, fields, name="Register Tenant", submit_text="Register", on_submit=self.register_tenant, small=True, field_per_row=2)
        
        # Create tenant search popup
        search_button, search_popup_func = pe.popup_card(
            tenant_card,
            button_text="Search Tenants",
            title="Tenant Information Lookup",
            button_size="small"
        )
        
        def setup_search_popup():
            content = search_popup_func()
            
            search_entry = ctk.CTkEntry(
                content,
                placeholder_text="Enter Tenant ID, Name, Email, NI Number, or Phone",
                height=40,
                font=("Arial", 14)
            )
            search_entry.pack(fill="x", padx=20, pady=20)
            
            result_label = ctk.CTkLabel(
                content,
                text="",
                font=("Arial", 12),
                justify="left",
                anchor="nw"
            )
            
            def search_tenant():
                search_term = search_entry.get().strip()
                if not search_term:
                    result_label.configure(text="Please enter a search term")
                    result_label.pack(fill="both", expand=True, padx=20, pady=10)
                    return
                
                if search_term.isdigit():
                    info = self.get_tenant_info(int(search_term))
                    result_label.configure(text=info)
                    result_label.pack(fill="both", expand=True, padx=20, pady=10)
                else:
                    results = tenant_repo.search_tenants(search_term, location=self.location)
                    if results:
                        if len(results) == 1:
                            info = self.get_tenant_info(results[0]['tenant_ID'])
                            result_label.configure(text=info)
                        else:
                            text = f"Found {len(results)} tenants in {self.location}:\n\n"
                            for r in results:
                                text += f"ID: {r['tenant_ID']} - {r['name']} - {r['email']}\n"
                            result_label.configure(text=text)
                        result_label.pack(fill="both", expand=True, padx=20, pady=10)
                    else:
                        result_label.configure(text=f"No tenants found in {self.location}")
                        result_label.pack(fill="both", expand=True, padx=20, pady=10)
            
            pe.action_button(content, text="Search", command=search_tenant)
        
        search_button.configure(command=setup_search_popup)

    def load_maintenance_content(self, row):
        maintenance_card = pe.function_card(row, "Maintenance Requests", side="left")
        
        # Register maintenance request button with popup
        maint_button, maint_popup_func = pe.popup_card(
            maintenance_card,
            button_text="Register Request",
            title="Register Maintenance Request",
            small=True,
            button_size="medium"
        )
        
        def setup_maint_popup():
            from datetime import datetime
            content = maint_popup_func()
            
            scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
            scrollable.pack(fill="both", expand=True, padx=30, pady=20)
            
            entries = {}
            
            # Tenant ID
            tenant_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            tenant_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(tenant_frame, text="Tenant ID *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['tenant_id'] = ctk.CTkEntry(tenant_frame, height=40, font=("Arial", 14))
            entries['tenant_id'].pack(fill="x")
            
            # Apartment ID
            apt_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            apt_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(apt_frame, text="Apartment ID *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['apartment_id'] = ctk.CTkEntry(apt_frame, height=40, font=("Arial", 14))
            entries['apartment_id'].pack(fill="x")
            
            # Issue Description
            issue_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            issue_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(issue_frame, text="Issue Description *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['issue_description'] = ctk.CTkTextbox(issue_frame, height=100, font=("Arial", 14))
            entries['issue_description'].pack(fill="x")
            
            # Priority Level
            priority_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            priority_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(priority_frame, text="Priority Level *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 8))
            
            priority_var = ctk.StringVar(value="2")
            priority_options = ctk.CTkFrame(priority_frame, fg_color="transparent")
            priority_options.pack(fill="x")
            
            for level, label in [("3", "High"), ("2", "Medium"), ("1", "Low")]:
                ctk.CTkRadioButton(
                    priority_options,
                    text=label,
                    variable=priority_var,
                    value=level,
                    font=("Arial", 13),
                    fg_color=("#1a3c5c", "#4196E0"),
                    hover_color=("#0d2438", "#3380CC")
                ).pack(side="left", padx=(0, 20))
            
            entries['priority_level'] = priority_var
            
            # Status messages
            status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            status_frame.pack(fill="x", pady=(10, 0))
            
            error_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#C41E3A", "#FF6B6B"))
            success_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0"))
            
            def handle_submit():
                error_label.pack_forget()
                success_label.pack_forget()
                
                # Validate
                if not entries['tenant_id'].get().strip().isdigit():
                    error_label.configure(text="❌ Error: Valid Tenant ID is required")
                    error_label.pack(pady=10)
                    return
                
                if not entries['apartment_id'].get().strip().isdigit():
                    error_label.configure(text="❌ Error: Valid Apartment ID is required")
                    error_label.pack(pady=10)
                    return
                
                if not entries['issue_description'].get("1.0", "end").strip():
                    error_label.configure(text="❌ Error: Issue description is required")
                    error_label.pack(pady=10)
                    return
                
                # Submit
                values = {
                    'tenant_id': int(entries['tenant_id'].get().strip()),
                    'apartment_id': int(entries['apartment_id'].get().strip()),
                    'issue_description': entries['issue_description'].get("1.0", "end").strip(),
                    'priority_level': int(entries['priority_level'].get()),
                    'reported_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                result = self.register_maintenance_request(values)
                if result is True:
                    success_label.configure(text="✓ Maintenance request registered successfully!")
                    success_label.pack(pady=10)
                    entries['tenant_id'].delete(0, 'end')
                    entries['apartment_id'].delete(0, 'end')
                    entries['issue_description'].delete("1.0", "end")
                    entries['priority_level'].set("2")
                else:
                    error_label.configure(text=f"❌ {str(result)}")
                    error_label.pack(pady=10)
            
            submit_btn = ctk.CTkButton(
                scrollable,
                text="Register Maintenance Request",
                command=handle_submit,
                height=50,
                font=("Arial", 16, "bold"),
                fg_color=("#1a3c5c", "#4196E0"),
                hover_color=("#0d2438", "#3380CC")
            )
            submit_btn.pack(fill="x", pady=(20, 10))
        
        maint_button.configure(command=setup_maint_popup)
        
        # View requests button
        view_button, view_popup_func = pe.popup_card(
            maintenance_card,
            button_text="View Requests",
            title="All Maintenance Requests",
            small=False,
            button_size="medium"
        )
        
        def setup_view_popup():
            content = view_popup_func()
            
            scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
            scrollable.pack(fill="both", expand=True, padx=30, pady=20)
            
            def refresh_requests():
                # Clear existing content
                for widget in scrollable.winfo_children():
                    widget.destroy()
                
                requests = tenant_repo.get_all_maintenance_requests(location=self.location)
                
                if requests:
                    for req in requests:
                        req_frame = ctk.CTkFrame(scrollable, fg_color=("gray85", "gray20"), corner_radius=8)
                        req_frame.pack(fill="x", pady=(0, 10))
                        
                        status_color = ("#4196E0", "#3380CC") if req.get('completed') else ("#FFA500", "#FF8C00")
                        status_text = "✓ Completed" if req.get('completed') else "⏳ Pending"
                        
                        info_text = (
                            f"Request ID: {req.get('request_ID', 'N/A')}\n"
                            f"Tenant: {req.get('tenant_name', 'N/A')}\n"
                            f"Apartment: {req.get('apartment_address', 'N/A')}\n"
                            f"Issue: {req.get('issue_description', 'N/A')}\n"
                            f"Priority: {req.get('priority_level', 'N/A')}\n"
                            f"Reported: {req.get('reported_date', 'N/A')}\n"
                            f"Status: {status_text}"
                        )
                        
                        info_label = ctk.CTkLabel(
                            req_frame,
                            text=info_text,
                            font=("Arial", 12),
                            justify="left",
                            anchor="w"
                        )
                        info_label.pack(padx=15, pady=(15, 10), fill="x")
                        
                        # Button container
                        button_frame = ctk.CTkFrame(req_frame, fg_color="transparent")
                        button_frame.pack(fill="x", padx=15, pady=(0, 15))
                        
                        request_id = req.get('request_ID')
                        is_completed = req.get('completed')
                        
                        # Flag/Unflag button
                        flag_text = "Mark as Pending" if is_completed else "Mark as Completed"
                        flag_btn = ctk.CTkButton(
                            button_frame,
                            text=flag_text,
                            command=lambda rid=request_id, completed=is_completed: handle_flag_request(rid, completed),
                            height=35,
                            font=("Arial", 12, "bold"),
                            fg_color=("#4196E0", "#3380CC") if not is_completed else ("#FFA500", "#FF8C00"),
                            hover_color=("#3380CC", "#2570B8") if not is_completed else ("#FF8C00", "#E67E00"),
                            width=180
                        )
                        flag_btn.pack(side="left", padx=(0, 10))
                        
                        # Delete button
                        delete_btn = ctk.CTkButton(
                            button_frame,
                            text="Delete",
                            command=lambda rid=request_id: handle_delete_request(rid),
                            height=35,
                            font=("Arial", 12, "bold"),
                            fg_color=("#C41E3A", "#FF6B6B"),
                            hover_color=("#A01828", "#E65A5A"),
                            width=120
                        )
                        delete_btn.pack(side="left")
                else:
                    ctk.CTkLabel(
                        scrollable,
                        text="No maintenance requests found",
                        font=("Arial", 14)
                    ).pack(pady=20)
            
            def handle_flag_request(request_id, current_status):
                try:
                    new_status = 0 if current_status else 1
                    tenant_repo.update_maintenance_request_status(request_id, new_status)
                    refresh_requests()
                except Exception as e:
                    print(f"Error flagging request: {e}")
            
            def handle_delete_request(request_id):
                try:
                    tenant_repo.delete_maintenance_request(request_id)
                    refresh_requests()
                except Exception as e:
                    print(f"Error deleting request: {e}")
            
            refresh_requests()
        
        view_button.configure(command=setup_view_popup)

    def load_complaints_content(self, row):
        complaints_card = pe.function_card(row, "Complaints", side="left")
        
        # Register complaint button with popup
        complaint_button, complaint_popup_func = pe.popup_card(
            complaints_card,
            button_text="Register Complaint",
            title="Register Tenant Complaint",
            small=True,
            button_size="medium"
        )
        
        def setup_complaint_popup():
            from datetime import datetime
            content = complaint_popup_func()
            
            scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
            scrollable.pack(fill="both", expand=True, padx=30, pady=20)
            
            entries = {}
            
            # Tenant ID
            tenant_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            tenant_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(tenant_frame, text="Tenant ID *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['tenant_id'] = ctk.CTkEntry(tenant_frame, height=40, font=("Arial", 14))
            entries['tenant_id'].pack(fill="x")
            
            # Complaint Description
            desc_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            desc_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(desc_frame, text="Complaint Description *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['description'] = ctk.CTkTextbox(desc_frame, height=150, font=("Arial", 14))
            entries['description'].pack(fill="x")
            
            # Status messages
            status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            status_frame.pack(fill="x", pady=(10, 0))
            
            error_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#C41E3A", "#FF6B6B"))
            success_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0"))
            
            def handle_submit():
                error_label.pack_forget()
                success_label.pack_forget()
                
                # Validate
                if not entries['tenant_id'].get().strip().isdigit():
                    error_label.configure(text="❌ Error: Valid Tenant ID is required")
                    error_label.pack(pady=10)
                    return
                
                if not entries['description'].get("1.0", "end").strip():
                    error_label.configure(text="❌ Error: Complaint description is required")
                    error_label.pack(pady=10)
                    return
                
                # Submit
                values = {
                    'tenant_id': int(entries['tenant_id'].get().strip()),
                    'description': entries['description'].get("1.0", "end").strip(),
                    'date_submitted': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                result = self.register_complaint(values)
                if result is True:
                    success_label.configure(text="✓ Complaint registered successfully!")
                    success_label.pack(pady=10)
                    entries['tenant_id'].delete(0, 'end')
                    entries['description'].delete("1.0", "end")
                else:
                    error_label.configure(text=f"❌ {str(result)}")
                    error_label.pack(pady=10)
            
            submit_btn = ctk.CTkButton(
                scrollable,
                text="Register Complaint",
                command=handle_submit,
                height=50,
                font=("Arial", 16, "bold"),
                fg_color=("#1a3c5c", "#4196E0"),
                hover_color=("#0d2438", "#3380CC")
            )
            submit_btn.pack(fill="x", pady=(20, 10))
        
        complaint_button.configure(command=setup_complaint_popup)
        
        # View complaints button
        view_complaint_button, view_complaint_popup_func = pe.popup_card(
            complaints_card,
            button_text="View Complaints",
            title="All Tenant Complaints",
            small=False,
            button_size="medium"
        )
        
        def setup_view_complaint_popup():
            content = view_complaint_popup_func()
            
            scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
            scrollable.pack(fill="both", expand=True, padx=30, pady=20)
            
            def refresh_complaints():
                # Clear existing content
                for widget in scrollable.winfo_children():
                    widget.destroy()
                
                complaints = tenant_repo.get_all_complaints(location=self.location)
                
                if complaints:
                    for comp in complaints:
                        comp_frame = ctk.CTkFrame(scrollable, fg_color=("gray85", "gray20"), corner_radius=8)
                        comp_frame.pack(fill="x", pady=(0, 10))
                        
                        status_color = ("#4196E0", "#3380CC") if comp.get('resolved') else ("#FFA500", "#FF8C00")
                        status_text = "✓ Resolved" if comp.get('resolved') else "⏳ Pending"
                        
                        info_text = (
                            f"Complaint ID: {comp.get('complaint_ID', 'N/A')}\n"
                            f"Tenant: {comp.get('tenant_name', 'N/A')}\n"
                            f"Description: {comp.get('description', 'N/A')}\n"
                            f"Submitted: {comp.get('date_submitted', 'N/A')}\n"
                            f"Status: {status_text}"
                        )
                        
                        info_label = ctk.CTkLabel(
                            comp_frame,
                            text=info_text,
                            font=("Arial", 12),
                            justify="left",
                            anchor="w"
                        )
                        info_label.pack(padx=15, pady=(15, 10), fill="x")
                        
                        # Button container
                        button_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
                        button_frame.pack(fill="x", padx=15, pady=(0, 15))
                        
                        complaint_id = comp.get('complaint_ID')
                        is_resolved = comp.get('resolved')
                        
                        # Flag/Unflag button
                        flag_text = "Mark as Pending" if is_resolved else "Mark as Resolved"
                        flag_btn = ctk.CTkButton(
                            button_frame,
                            text=flag_text,
                            command=lambda cid=complaint_id, resolved=is_resolved: handle_flag_complaint(cid, resolved),
                            height=35,
                            font=("Arial", 12, "bold"),
                            fg_color=("#4196E0", "#3380CC") if not is_resolved else ("#FFA500", "#FF8C00"),
                            hover_color=("#3380CC", "#2570B8") if not is_resolved else ("#FF8C00", "#E67E00"),
                            width=180
                        )
                        flag_btn.pack(side="left", padx=(0, 10))
                        
                        # Delete button
                        delete_btn = ctk.CTkButton(
                            button_frame,
                            text="Delete",
                            command=lambda cid=complaint_id: handle_delete_complaint(cid),
                            height=35,
                            font=("Arial", 12, "bold"),
                            fg_color=("#C41E3A", "#FF6B6B"),
                            hover_color=("#A01828", "#E65A5A"),
                            width=120
                        )
                        delete_btn.pack(side="left")
                else:
                    ctk.CTkLabel(
                        scrollable,
                        text="No complaints found",
                        font=("Arial", 14)
                    ).pack(pady=20)
            
            def handle_flag_complaint(complaint_id, current_status):
                try:
                    new_status = 0 if current_status else 1
                    tenant_repo.update_complaint_status(complaint_id, new_status)
                    refresh_complaints()
                except Exception as e:
                    print(f"Error flagging complaint: {e}")
            
            def handle_delete_complaint(complaint_id):
                try:
                    tenant_repo.delete_complaint(complaint_id)
                    refresh_complaints()
                except Exception as e:
                    print(f"Error deleting complaint: {e}")
            
            refresh_complaints()
        
        view_complaint_button.configure(command=setup_view_complaint_popup)
# ============================= ^ Homepage UI Content ^ =====================================
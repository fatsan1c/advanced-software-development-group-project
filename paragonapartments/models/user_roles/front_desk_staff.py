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
        
        first_name = values.get('First Name', '')
        last_name = values.get('Last Name', '')
        date_of_birth = values.get('Date of Birth', '')
        ni_number = values.get('NI Number', '')
        email = values.get('Email', '')
        phone = values.get('Phone', '')
        occupation = values.get('Occupation', '')
        annual_salary = values.get('Annual Salary', '')
        pets = values.get('Pets', 'N')
        right_to_rent = values.get('Right to Rent', 'N')
        credit_check = values.get('Credit Check', 'Pending')
        
        city = values.get('City', '')
        apartment_full = values.get('Apartment', '')
        # Extract apartment address from formatted string (e.g., "Apartment 6 - 2 beds - £850/month")
        apartment = apartment_full.split(' - ')[0] if ' - ' in apartment_full else apartment_full
        start_date = values.get('Contract Start Date', '')
        end_date = values.get('Contract End Date', '')
        
        try:
            # Convert annual_salary to float if provided
            salary_value = float(annual_salary) if annual_salary and annual_salary.strip() else None
            
            # Create tenant record
            tenant_repo.create_tenant(
                first_name, last_name, date_of_birth, ni_number, email, phone,
                occupation, salary_value, pets, right_to_rent, credit_check
            )
            
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
                f"Name: {result['first_name']} {result['last_name']}\n"
                f"Date of Birth: {result.get('date_of_birth', 'N/A')}\n"
                f"NI Number: {result['NI_number']}\n"
                f"Email: {result['email']}\n"
                f"Phone: {result['phone']}\n"
                f"Occupation: {result.get('occupation', 'N/A')}\n"
                f"Annual Salary: £{result.get('annual_salary', 'N/A') if result.get('annual_salary') else 'N/A'}\n"
                f"Pets: {result.get('pets', 'N/A')}\n"
                f"Right to Rent: {result.get('right_to_rent', 'N/A')}\n"
                f"Credit Check: {result.get('credit_check', 'N/A')}"
            )
            return info
        return "Tenant not found or not in your location"

    def update_tenant(self, tenant_id, values):
        """Update existing tenant information."""
        try:
            # Prepare update fields
            update_fields = {}
            
            if values.get('First Name'):
                update_fields['first_name'] = values['First Name']
            if values.get('Last Name'):
                update_fields['last_name'] = values['Last Name']
            if values.get('Date of Birth'):
                update_fields['date_of_birth'] = values['Date of Birth']
            if values.get('NI Number'):
                update_fields['NI_number'] = values['NI Number']
            if values.get('Email'):
                update_fields['email'] = values['Email']
            if values.get('Phone'):
                update_fields['phone'] = values['Phone']
            if values.get('Occupation'):
                update_fields['occupation'] = values['Occupation']
            if values.get('Annual Salary'):
                update_fields['annual_salary'] = float(values['Annual Salary']) if values['Annual Salary'].strip() else None
            if values.get('Pets'):
                update_fields['pets'] = values['Pets']
            if values.get('Right to Rent'):
                update_fields['right_to_rent'] = values['Right to Rent']
            if values.get('Credit Check'):
                update_fields['credit_check'] = values['Credit Check']
            
            # Update tenant
            tenant_repo.update_tenant(tenant_id, **update_fields)
            return True
        except Exception as e:
            return f"Failed to update tenant: {str(e)}"

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

        container = pe.scrollable_container(parent=home_page)
        
        # First row - Tenant Management
        row1 = pe.row_container(parent=container)
        self.load_tenant_content(row1)
        
        # Second row - Apartment Search
        row2 = pe.row_container(parent=container)
        self.load_apartment_search_content(row2)
        
        # Third row - Maintenance and Complaints
        row3 = pe.row_container(parent=container)
        self.load_maintenance_content(row3)
        self.load_complaints_content(row3)

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
        
        # Create tenant registration form with popup
        register_button, register_popup_func = pe.popup_card(
            tenant_card,
            button_text="Register New Tenant",
            title="Tenant Registration",
            small=False,
            button_size="large"
        )
        
        def setup_registration_popup():
            content = register_popup_func()
            
            scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
            scrollable.pack(fill="both", expand=True, padx=30, pady=20)
            
            entries = {}
            
            # === PERSONAL INFORMATION SECTION ===
            section_label = ctk.CTkLabel(
                scrollable, 
                text="━━━━━━━━━━━━ Personal Information ━━━━━━━━━━━━", 
                font=("Arial", 14, "bold"),
                text_color=("#1a3c5c", "#4196E0")
            )
            section_label.pack(fill="x", pady=(0, 15))
            
            # First Name
            fname_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            fname_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(fname_frame, text="First Name *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['First Name'] = ctk.CTkEntry(fname_frame, height=40, font=("Arial", 14), placeholder_text="Enter first name")
            entries['First Name'].pack(fill="x")
            
            # Last Name
            lname_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            lname_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(lname_frame, text="Last Name *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Last Name'] = ctk.CTkEntry(lname_frame, height=40, font=("Arial", 14), placeholder_text="Enter last name")
            entries['Last Name'].pack(fill="x")
            
            # Date of Birth
            dob_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            dob_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(dob_frame, text="Date of Birth *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Date of Birth'] = ctk.CTkEntry(dob_frame, height=40, font=("Arial", 14), placeholder_text="YYYY-MM-DD (e.g., 1990-01-15)")
            entries['Date of Birth'].pack(fill="x")
            
            # NI Number
            ni_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            ni_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(ni_frame, text="National Insurance Number *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['NI Number'] = ctk.CTkEntry(ni_frame, height=40, font=("Arial", 14), placeholder_text="AB123456C")
            entries['NI Number'].pack(fill="x")
            
            # === CONTACT INFORMATION SECTION ===
            section_label2 = ctk.CTkLabel(
                scrollable, 
                text="━━━━━━━━━━━━ Contact Information ━━━━━━━━━━━━", 
                font=("Arial", 14, "bold"),
                text_color=("#1a3c5c", "#4196E0")
            )
            section_label2.pack(fill="x", pady=(15, 15))
            
            # Email
            email_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            email_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(email_frame, text="Email Address *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Email'] = ctk.CTkEntry(email_frame, height=40, font=("Arial", 14), placeholder_text="example@email.com")
            entries['Email'].pack(fill="x")
            
            # Phone
            phone_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            phone_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(phone_frame, text="Phone Number *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Phone'] = ctk.CTkEntry(phone_frame, height=40, font=("Arial", 14), placeholder_text="07123456789")
            entries['Phone'].pack(fill="x")
            
            # === TENANT DETAILS SECTION ===
            section_label3 = ctk.CTkLabel(
                scrollable, 
                text="━━━━━━━━━━━━ Tenant Details ━━━━━━━━━━━━", 
                font=("Arial", 14, "bold"),
                text_color=("#1a3c5c", "#4196E0")
            )
            section_label3.pack(fill="x", pady=(15, 15))
            
            # Occupation
            occ_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            occ_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(occ_frame, text="Occupation", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Occupation'] = ctk.CTkEntry(occ_frame, height=40, font=("Arial", 14), placeholder_text="Job title (optional)")
            entries['Occupation'].pack(fill="x")
            
            # Annual Salary
            salary_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            salary_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(salary_frame, text="Annual Salary (£)", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Annual Salary'] = ctk.CTkEntry(salary_frame, height=40, font=("Arial", 14), placeholder_text="e.g., 30000 (optional)")
            entries['Annual Salary'].pack(fill="x")
            
            # Pets
            pets_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            pets_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(pets_frame, text="Pets *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Pets'] = ctk.CTkOptionMenu(pets_frame, values=['N', 'Y'], height=40, font=("Arial", 14), fg_color=("#1a3c5c", "#4196E0"), button_color=("#0d2438", "#3380CC"), button_hover_color=("#0a1d2e", "#2570B8"))
            entries['Pets'].set('N')
            entries['Pets'].pack(fill="x")
            
            # Right to Rent
            rtr_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            rtr_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(rtr_frame, text="Right to Rent *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Right to Rent'] = ctk.CTkOptionMenu(rtr_frame, values=['N', 'Y'], height=40, font=("Arial", 14), fg_color=("#1a3c5c", "#4196E0"), button_color=("#0d2438", "#3380CC"), button_hover_color=("#0a1d2e", "#2570B8"))
            entries['Right to Rent'].set('N')
            entries['Right to Rent'].pack(fill="x")
            
            # Credit Check
            cc_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            cc_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(cc_frame, text="Credit Check Status *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Credit Check'] = ctk.CTkOptionMenu(cc_frame, values=['Pending', 'Approved', 'Rejected'], height=40, font=("Arial", 14), fg_color=("#1a3c5c", "#4196E0"), button_color=("#0d2438", "#3380CC"), button_hover_color=("#0a1d2e", "#2570B8"))
            entries['Credit Check'].set('Pending')
            entries['Credit Check'].pack(fill="x")
            
            # === PROPERTY & LEASE SECTION ===
            section_label4 = ctk.CTkLabel(
                scrollable, 
                text="━━━━━━━━━━━━ Property & Lease Information ━━━━━━━━━━━━", 
                font=("Arial", 14, "bold"),
                text_color=("#1a3c5c", "#4196E0")
            )
            section_label4.pack(fill="x", pady=(15, 15))
            
            # City
            city_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            city_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(city_frame, text="Location *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['City'] = ctk.CTkOptionMenu(city_frame, values=[self.location], height=40, font=("Arial", 14), fg_color=("#1a3c5c", "#4196E0"), button_color=("#0d2438", "#3380CC"), button_hover_color=("#0a1d2e", "#2570B8"))
            entries['City'].set(self.location)
            entries['City'].pack(fill="x")
            
            # Apartment
            apt_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            apt_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(apt_frame, text="Select Apartment *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            apt_options = apartment_options if apartment_options else ['No vacant apartments']
            entries['Apartment'] = ctk.CTkOptionMenu(apt_frame, values=apt_options, height=40, font=("Arial", 14), fg_color=("#1a3c5c", "#4196E0"), button_color=("#0d2438", "#3380CC"), button_hover_color=("#0a1d2e", "#2570B8"))
            entries['Apartment'].set(apt_options[0])
            entries['Apartment'].pack(fill="x")
            
            # Contract Start Date
            start_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            start_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(start_frame, text="Contract Start Date *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Contract Start Date'] = ctk.CTkEntry(start_frame, height=40, font=("Arial", 14), placeholder_text="YYYY-MM-DD (e.g., 2026-03-01)")
            entries['Contract Start Date'].pack(fill="x")
            
            # Contract End Date
            end_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            end_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(end_frame, text="Contract End Date *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['Contract End Date'] = ctk.CTkEntry(end_frame, height=40, font=("Arial", 14), placeholder_text="YYYY-MM-DD (e.g., 2027-03-01)")
            entries['Contract End Date'].pack(fill="x")
            
            # Status messages
            status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            status_frame.pack(fill="x", pady=(15, 0))
            
            error_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#C41E3A", "#FF6B6B"))
            success_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0"))
            
            def handle_submit():
                error_label.pack_forget()
                success_label.pack_forget()
                
                # Validate required fields
                required_fields = ['First Name', 'Last Name', 'Date of Birth', 'NI Number', 'Email', 'Phone', 'Contract Start Date', 'Contract End Date']
                for field in required_fields:
                    value = entries[field].get().strip() if field in entries else ""
                    if not value:
                        error_label.configure(text=f"❌ Error: {field} is required")
                        error_label.pack(pady=10)
                        return
                
                # Check if apartment is available
                if entries['Apartment'].get() == 'No vacant apartments':
                    error_label.configure(text="❌ Error: No apartments available in this location")
                    error_label.pack(pady=10)
                    return
                
                # Collect values
                values = {}
                for field_name, entry_widget in entries.items():
                    if isinstance(entry_widget, ctk.CTkEntry):
                        values[field_name] = entry_widget.get().strip()
                    elif isinstance(entry_widget, ctk.CTkOptionMenu):
                        values[field_name] = entry_widget.get()
                
                # Submit
                result = self.register_tenant(values)
                if result is True:
                    success_label.configure(text="✓ Tenant registered successfully!")
                    success_label.pack(pady=10)
                    # Clear all entry fields
                    for field_name, entry_widget in entries.items():
                        if isinstance(entry_widget, ctk.CTkEntry):
                            entry_widget.delete(0, 'end')
                        elif isinstance(entry_widget, ctk.CTkOptionMenu) and field_name not in ['City']:
                            if field_name == 'Pets' or field_name == 'Right to Rent':
                                entry_widget.set('N')
                            elif field_name == 'Credit Check':
                                entry_widget.set('Pending')
                else:
                    error_label.configure(text=f"❌ {str(result)}")
                    error_label.pack(pady=10)
            
            submit_btn = ctk.CTkButton(
                scrollable,
                text="Register Tenant",
                command=handle_submit,
                height=50,
                font=("Arial", 16, "bold"),
                fg_color=("#1a3c5c", "#4196E0"),
                hover_color=("#0d2438", "#3380CC")
            )
            submit_btn.pack(fill="x", pady=(20, 10))
        
        register_button.configure(command=setup_registration_popup)
        
        # Create tenant search popup
        search_button, search_popup_func = pe.popup_card(
            tenant_card,
            button_text="Search Tenants",
            title="Tenant Information Lookup",
            small=False,
            button_size="large"
        )
        
        def setup_search_popup():
            content = search_popup_func()
            
            # Search input section
            search_frame = ctk.CTkFrame(content, fg_color="transparent")
            search_frame.pack(fill="x", padx=30, pady=(20, 10))
            
            ctk.CTkLabel(
                search_frame,
                text="Search by ID, Name, Email, NI Number, or Phone",
                font=("Arial", 13, "bold"),
                text_color=("#1a3c5c", "#4196E0")
            ).pack(anchor="w", pady=(0, 8))
            
            search_input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
            search_input_frame.pack(fill="x")
            
            search_entry = ctk.CTkEntry(
                search_input_frame,
                placeholder_text="Enter search term...",
                height=45,
                font=("Arial", 14)
            )
            search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            search_btn = ctk.CTkButton(
                search_input_frame,
                text="Search",
                command=lambda: perform_search(),
                height=45,
                width=120,
                font=("Arial", 14, "bold"),
                fg_color=("#1a3c5c", "#4196E0"),
                hover_color=("#0d2438", "#3380CC")
            )
            search_btn.pack(side="right", padx=(0, 10))
            
            # View All button
            view_all_btn = ctk.CTkButton(
                search_input_frame,
                text="View All",
                command=lambda: view_all_tenants(),
                height=45,
                width=120,
                font=("Arial", 14, "bold"),
                fg_color=("#0d7377", "#14A9AF"),
                hover_color=("#0a5d61", "#108B90")
            )
            view_all_btn.pack(side="right")
            
            # Results area
            results_frame = ctk.CTkScrollableFrame(content, fg_color="transparent")
            results_frame.pack(fill="both", expand=True, padx=30, pady=(10, 20))
            
            def display_tenant_results(results, search_term=""):
                """Helper function to display tenant results"""
                # Clear previous results
                for widget in results_frame.winfo_children():
                    widget.destroy()
                
                if not results:
                    no_results = ctk.CTkLabel(
                        results_frame,
                        text=f"❌ No tenants found{' matching ' + repr(search_term) if search_term else ''} in {self.location}",
                        font=("Arial", 14),
                        text_color=("#C41E3A", "#FF6B6B")
                    )
                    no_results.pack(pady=20)
                    return
                
                # Display header
                header_text = f"✓ Found {len(results)} tenant{'s' if len(results) > 1 else ''}"
                if search_term:
                    header_text += f" matching '{search_term}'"
                else:
                    header_text += f" in {self.location}"
                    
                header = ctk.CTkLabel(
                    results_frame,
                    text=header_text,
                    font=("Arial", 15, "bold"),
                    text_color=("#1a3c5c", "#4196E0")
                )
                header.pack(pady=(0, 15))
                
                # Display each tenant in a card
                for tenant in results:
                    tenant_card_frame = ctk.CTkFrame(
                        results_frame,
                        fg_color=("gray90", "gray17"),
                        corner_radius=10
                    )
                    tenant_card_frame.pack(fill="x", pady=(0, 12))
                    
                    # Content frame with padding
                    content_frame = ctk.CTkFrame(tenant_card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=20, pady=15)
                    
                    # Tenant name as header
                    name = f"{tenant.get('first_name', '')} {tenant.get('last_name', '')}".strip()
                    name_label = ctk.CTkLabel(
                        content_frame,
                        text=name,
                        font=("Arial", 16, "bold"),
                        text_color=("#1a3c5c", "#4196E0"),
                        anchor="w"
                    )
                    name_label.pack(fill="x", pady=(0, 8))
                    
                    # Tenant details in a grid
                    details_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    details_frame.pack(fill="x", pady=(0, 10))
                    
                    # Left column
                    left_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                    left_col.pack(side="left", fill="both", expand=True)
                    
                    ctk.CTkLabel(
                        left_col,
                        text=f"🆔 Tenant ID: {tenant.get('tenant_ID', 'N/A')}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(
                        left_col,
                        text=f"📧 Email: {tenant.get('email', 'N/A')}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(
                        left_col,
                        text=f"📱 Phone: {tenant.get('phone', 'N/A')}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
                    
                    # Right column
                    right_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                    right_col.pack(side="right", fill="both", expand=True)
                    
                    ctk.CTkLabel(
                        right_col,
                        text=f"🎂 DOB: {tenant.get('date_of_birth', 'N/A')}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(
                        right_col,
                        text=f"🆔 NI: {tenant.get('NI_number', 'N/A')}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(
                        right_col,
                        text=f"💼 Occupation: {tenant.get('occupation', 'N/A') or 'N/A'}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
                    
                    # View full details button
                    tenant_id = tenant.get('tenant_ID')
                    
                    def create_view_details(tid):
                        def view_full_details():
                            # Clear results and show full details
                            for widget in results_frame.winfo_children():
                                widget.destroy()
                            
                            info_text = self.get_tenant_info(tid)
                            
                            # Back button
                            back_btn = ctk.CTkButton(
                                results_frame,
                                text="← Back to Search Results",
                                command=lambda: display_tenant_results(results, search_term),
                                height=40,
                                font=("Arial", 13, "bold"),
                                fg_color=("gray75", "gray30"),
                                hover_color=("gray65", "gray25")
                            )
                            back_btn.pack(fill="x", pady=(0, 15))
                            
                            # Full details card
                            details_card = ctk.CTkFrame(
                                results_frame,
                                fg_color=("gray90", "gray17"),
                                corner_radius=10
                            )
                            details_card.pack(fill="both", expand=True)
                            
                            info_label = ctk.CTkLabel(
                                details_card,
                                text=info_text,
                                font=("Arial", 13),
                                justify="left",
                                anchor="nw"
                            )
                            info_label.pack(padx=25, pady=20, fill="both", expand=True)
                        
                        return view_full_details
                    
                    def create_edit_tenant(tid, tenant_data):
                        def edit_tenant():
                            # Create edit popup
                            edit_popup = ctk.CTkToplevel(content)
                            edit_popup.title("Edit Tenant Information")
                            edit_popup.geometry("700x800")
                            edit_popup.transient(content)
                            edit_popup.grab_set()
                            
                            scrollable_edit = ctk.CTkScrollableFrame(edit_popup, fg_color="transparent")
                            scrollable_edit.pack(fill="both", expand=True, padx=30, pady=20)
                            
                            entries = {}
                            
                            # Header
                            ctk.CTkLabel(
                                scrollable_edit,
                                text=f"✏️ Editing Tenant #{tid}",
                                font=("Arial", 18, "bold"),
                                text_color=("#1a3c5c", "#4196E0")
                            ).pack(pady=(0, 20))
                            
                            # Personal Information
                            section_label = ctk.CTkLabel(
                                scrollable_edit, 
                                text="━━━━━━━━━━━━ Personal Information ━━━━━━━━━━━━", 
                                font=("Arial", 14, "bold"),
                                text_color=("#1a3c5c", "#4196E0")
                            )
                            section_label.pack(fill="x", pady=(0, 15))
                            
                            # First Name
                            fname_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            fname_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(fname_frame, text="First Name *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['First Name'] = ctk.CTkEntry(fname_frame, height=40, font=("Arial", 14))
                            entries['First Name'].insert(0, tenant_data.get('first_name', ''))
                            entries['First Name'].pack(fill="x")
                            
                            # Last Name
                            lname_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            lname_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(lname_frame, text="Last Name *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['Last Name'] = ctk.CTkEntry(lname_frame, height=40, font=("Arial", 14))
                            entries['Last Name'].insert(0, tenant_data.get('last_name', ''))
                            entries['Last Name'].pack(fill="x")
                            
                            # Date of Birth
                            dob_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            dob_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(dob_frame, text="Date of Birth *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['Date of Birth'] = ctk.CTkEntry(dob_frame, height=40, font=("Arial", 14))
                            entries['Date of Birth'].insert(0, tenant_data.get('date_of_birth', ''))
                            entries['Date of Birth'].pack(fill="x")
                            
                            # NI Number
                            ni_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            ni_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(ni_frame, text="National Insurance Number *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['NI Number'] = ctk.CTkEntry(ni_frame, height=40, font=("Arial", 14))
                            entries['NI Number'].insert(0, tenant_data.get('NI_number', ''))
                            entries['NI Number'].pack(fill="x")
                            
                            # Contact Information
                            section_label2 = ctk.CTkLabel(
                                scrollable_edit, 
                                text="━━━━━━━━━━━━ Contact Information ━━━━━━━━━━━━", 
                                font=("Arial", 14, "bold"),
                                text_color=("#1a3c5c", "#4196E0")
                            )
                            section_label2.pack(fill="x", pady=(15, 15))
                            
                            # Email
                            email_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            email_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(email_frame, text="Email Address *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['Email'] = ctk.CTkEntry(email_frame, height=40, font=("Arial", 14))
                            entries['Email'].insert(0, tenant_data.get('email', ''))
                            entries['Email'].pack(fill="x")
                            
                            # Phone
                            phone_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            phone_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(phone_frame, text="Phone Number *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['Phone'] = ctk.CTkEntry(phone_frame, height=40, font=("Arial", 14))
                            entries['Phone'].insert(0, tenant_data.get('phone', ''))
                            entries['Phone'].pack(fill="x")
                            
                            # Tenant Details
                            section_label3 = ctk.CTkLabel(
                                scrollable_edit, 
                                text="━━━━━━━━━━━━ Tenant Details ━━━━━━━━━━━━", 
                                font=("Arial", 14, "bold"),
                                text_color=("#1a3c5c", "#4196E0")
                            )
                            section_label3.pack(fill="x", pady=(15, 15))
                            
                            # Occupation
                            occ_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            occ_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(occ_frame, text="Occupation", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['Occupation'] = ctk.CTkEntry(occ_frame, height=40, font=("Arial", 14))
                            entries['Occupation'].insert(0, tenant_data.get('occupation', '') or '')
                            entries['Occupation'].pack(fill="x")
                            
                            # Annual Salary
                            salary_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            salary_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(salary_frame, text="Annual Salary (£)", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['Annual Salary'] = ctk.CTkEntry(salary_frame, height=40, font=("Arial", 14))
                            salary_val = str(tenant_data.get('annual_salary', '')) if tenant_data.get('annual_salary') else ''
                            entries['Annual Salary'].insert(0, salary_val)
                            entries['Annual Salary'].pack(fill="x")
                            
                            # Pets
                            pets_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            pets_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(pets_frame, text="Pets *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['Pets'] = ctk.CTkOptionMenu(pets_frame, values=['N', 'Y'], height=40, font=("Arial", 14), fg_color=("#1a3c5c", "#4196E0"))
                            entries['Pets'].set(tenant_data.get('pets', 'N'))
                            entries['Pets'].pack(fill="x")
                            
                            # Right to Rent
                            rtr_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            rtr_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(rtr_frame, text="Right to Rent *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['Right to Rent'] = ctk.CTkOptionMenu(rtr_frame, values=['N', 'Y'], height=40, font=("Arial", 14), fg_color=("#1a3c5c", "#4196E0"))
                            entries['Right to Rent'].set(tenant_data.get('right_to_rent', 'N'))
                            entries['Right to Rent'].pack(fill="x")
                            
                            # Credit Check
                            cc_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            cc_frame.pack(fill="x", pady=(0, 12))
                            ctk.CTkLabel(cc_frame, text="Credit Check Status *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
                            entries['Credit Check'] = ctk.CTkOptionMenu(cc_frame, values=['Pending', 'Approved', 'Rejected'], height=40, font=("Arial", 14), fg_color=("#1a3c5c", "#4196E0"))
                            entries['Credit Check'].set(tenant_data.get('credit_check', 'Pending'))
                            entries['Credit Check'].pack(fill="x")
                            
                            # Status messages
                            status_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            status_frame.pack(fill="x", pady=(15, 0))
                            
                            error_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#C41E3A", "#FF6B6B"))
                            success_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#2D862D", "#4CAF50"))
                            
                            def handle_update():
                                error_label.pack_forget()
                                success_label.pack_forget()
                                
                                # Validate required fields
                                required_fields = ['First Name', 'Last Name', 'Date of Birth', 'NI Number', 'Email', 'Phone']
                                for field in required_fields:
                                    value = entries[field].get().strip() if isinstance(entries[field], ctk.CTkEntry) else ""
                                    if not value:
                                        error_label.configure(text=f"❌ Error: {field} is required")
                                        error_label.pack(pady=10)
                                        return
                                
                                # Collect values
                                values = {}
                                for field_name, entry_widget in entries.items():
                                    if isinstance(entry_widget, ctk.CTkEntry):
                                        values[field_name] = entry_widget.get().strip()
                                    elif isinstance(entry_widget, ctk.CTkOptionMenu):
                                        values[field_name] = entry_widget.get()
                                
                                # Submit
                                result = self.update_tenant(tid, values)
                                if result is True:
                                    success_label.configure(text="✅ Tenant updated successfully!")
                                    success_label.pack(pady=10)
                                    # Refresh search results after a delay
                                    edit_popup.after(1500, edit_popup.destroy)
                                    edit_popup.after(1500, lambda: perform_search())
                                else:
                                    error_label.configure(text=f"❌ {str(result)}")
                                    error_label.pack(pady=10)
                            
                            # Buttons frame
                            buttons_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                            buttons_frame.pack(fill="x", pady=(20, 10))
                            
                            # Update button
                            update_btn = ctk.CTkButton(
                                buttons_frame,
                                text="💾 Save Changes",
                                command=handle_update,
                                height=50,
                                font=("Arial", 16, "bold"),
                                fg_color=("#1a3c5c", "#4196E0"),
                                hover_color=("#0d2438", "#3380CC")
                            )
                            update_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
                            
                            # Cancel button
                            cancel_btn = ctk.CTkButton(
                                buttons_frame,
                                text="❌ Cancel",
                                command=edit_popup.destroy,
                                height=50,
                                font=("Arial", 16, "bold"),
                                fg_color=("gray70", "gray30"),
                                hover_color=("gray60", "gray25")
                            )
                            cancel_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
                        
                        return edit_tenant
                    
                    # Buttons frame
                    buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    buttons_frame.pack(fill="x", pady=(5, 0))
                    
                    view_btn = ctk.CTkButton(
                        buttons_frame,
                        text="👁️ View Full Details",
                        command=create_view_details(tenant_id),
                        height=38,
                        font=("Arial", 13, "bold"),
                        fg_color=("#1a3c5c", "#4196E0"),
                        hover_color=("#0d2438", "#3380CC")
                    )
                    view_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
                    
                    edit_btn = ctk.CTkButton(
                        buttons_frame,
                        text="✏️ Edit Tenant",
                        command=create_edit_tenant(tenant_id, tenant),
                        height=38,
                        font=("Arial", 13, "bold"),
                        fg_color=("#0d7377", "#14A9AF"),
                        hover_color=("#0a5d61", "#108B90")
                    )
                    edit_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
            
            def perform_search():
                search_term = search_entry.get().strip()
                if not search_term:
                    # Clear previous results
                    for widget in results_frame.winfo_children():
                        widget.destroy()
                    error_msg = ctk.CTkLabel(
                        results_frame,
                        text="⚠️ Please enter a search term",
                        font=("Arial", 14),
                        text_color=("#FFA500", "#FF8C00")
                    )
                    error_msg.pack(pady=20)
                    return
                
                # Search by ID if numeric
                if search_term.isdigit():
                    result = tenant_repo.get_tenant_by_id(int(search_term), location=self.location)
                    results = [result] if result else []
                else:
                    # Search by name, email, etc.
                    results = tenant_repo.search_tenants(search_term, location=self.location)
                
                display_tenant_results(results, search_term)
            
            def view_all_tenants():
                """View all tenants in this location"""
                search_entry.delete(0, 'end')  # Clear search box
                results = tenant_repo.get_all_tenants(location=self.location)
                display_tenant_results(results, "")
            
            # Bind Enter key to search
            search_entry.bind("<Return>", lambda e: perform_search())
            
            # Show initial message
            initial_msg = ctk.CTkLabel(
                results_frame,
                text="👆 Enter a search term above to find tenants",
                font=("Arial", 14),
                text_color=("gray50", "gray60")
            )
            initial_msg.pack(pady=40)
        
        search_button.configure(command=setup_search_popup)

    def load_apartment_search_content(self, row):
        from database_operations.repos import apartment_repository as apt_repo
        
        apartment_card = pe.function_card(row, "Apartment Search", side="left")
        
        # Search apartments button with popup
        search_apt_button, search_apt_popup_func = pe.popup_card(
            apartment_card,
            button_text="Search Apartments",
            title="Find Available Apartments",
            small=False,
            button_size="large"
        )
        
        def setup_apartment_search_popup():
            content = search_apt_popup_func()
            
            # Filter section
            filter_frame = ctk.CTkFrame(content, fg_color="transparent")
            filter_frame.pack(fill="x", padx=30, pady=(20, 10))
            
            ctk.CTkLabel(
                filter_frame,
                text="🔍 Search Filters",
                font=("Arial", 16, "bold"),
                text_color=("#1a3c5c", "#4196E0")
            ).pack(anchor="w", pady=(0, 15))
            
            filters = {}
            
            # Location filter
            loc_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
            loc_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(loc_frame, text="📍 Location", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            filters['location'] = ctk.CTkOptionMenu(
                loc_frame, 
                values=['All', self.location], 
                height=40, 
                font=("Arial", 14),
                fg_color=("#1a3c5c", "#4196E0")
            )
            filters['location'].set(self.location)
            filters['location'].pack(fill="x")
            
            # Number of beds filter
            beds_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
            beds_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(beds_frame, text="🛏️ Number of Bedrooms", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            filters['beds'] = ctk.CTkOptionMenu(
                beds_frame, 
                values=['Any', '1', '2', '3', '4', '5+'], 
                height=40, 
                font=("Arial", 14),
                fg_color=("#1a3c5c", "#4196E0")
            )
            filters['beds'].set('Any')
            filters['beds'].pack(fill="x")
            
            # Availability filter
            status_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
            status_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(status_frame, text="✅ Availability", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            filters['status'] = ctk.CTkOptionMenu(
                status_frame, 
                values=['All', 'Vacant', 'Occupied'], 
                height=40, 
                font=("Arial", 14),
                fg_color=("#1a3c5c", "#4196E0")
            )
            filters['status'].set('All')
            filters['status'].pack(fill="x")
            
            # Price range filter
            price_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
            price_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(price_frame, text="💰 Max Monthly Rent (£)", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            filters['max_rent'] = ctk.CTkEntry(
                price_frame, 
                height=40, 
                font=("Arial", 14), 
                placeholder_text="Leave blank for no limit"
            )
            filters['max_rent'].pack(fill="x")
            
            # Search button
            search_btn = ctk.CTkButton(
                filter_frame,
                text="🔎 Search Apartments",
                command=lambda: perform_apartment_search(),
                height=50,
                font=("Arial", 16, "bold"),
                fg_color=("#1a3c5c", "#4196E0"),
                hover_color=("#0d2438", "#3380CC")
            )
            search_btn.pack(fill="x", pady=(10, 0))
            
            # Results area
            results_frame = ctk.CTkScrollableFrame(content, fg_color="transparent")
            results_frame.pack(fill="both", expand=True, padx=30, pady=(10, 20))
            
            def display_apartment_results(apartments):
                """Display apartment search results"""
                # Clear previous results
                for widget in results_frame.winfo_children():
                    widget.destroy()
                
                if not apartments:
                    no_results = ctk.CTkLabel(
                        results_frame,
                        text="❌ No apartments found matching your criteria",
                        font=("Arial", 14),
                        text_color=("#C41E3A", "#FF6B6B")
                    )
                    no_results.pack(pady=20)
                    return
                
                # Display header
                header_text = f"✓ Found {len(apartments)} apartment{'s' if len(apartments) > 1 else ''}"
                header = ctk.CTkLabel(
                    results_frame,
                    text=header_text,
                    font=("Arial", 15, "bold"),
                    text_color=("#1a3c5c", "#4196E0")
                )
                header.pack(pady=(0, 15))
                
                # Display each apartment in a card
                for apt in apartments:
                    apt_card_frame = ctk.CTkFrame(
                        results_frame,
                        fg_color=("gray90", "gray17"),
                        corner_radius=10
                    )
                    apt_card_frame.pack(fill="x", pady=(0, 12))
                    
                    # Content frame with padding
                    content_frame = ctk.CTkFrame(apt_card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=20, pady=15)
                    
                    # Header with address and status
                    header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    header_frame.pack(fill="x", pady=(0, 10))
                    
                    # Address
                    address_label = ctk.CTkLabel(
                        header_frame,
                        text=f"🏠 {apt.get('apartment_address', 'N/A')}",
                        font=("Arial", 16, "bold"),
                        text_color=("#1a3c5c", "#4196E0"),
                        anchor="w"
                    )
                    address_label.pack(side="left", fill="x", expand=True)
                    
                    # Status badge
                    status = apt.get('status', 'Unknown')
                    status_color = ("#2D862D", "#4CAF50") if status == 'Vacant' else ("#C41E3A", "#FF6B6B")
                    status_text = f"{'✅ ' if status == 'Vacant' else '🔴 '}{status.upper()}"
                    
                    status_badge = ctk.CTkLabel(
                        header_frame,
                        text=status_text,
                        font=("Arial", 11, "bold"),
                        text_color="white",
                        fg_color=status_color,
                        corner_radius=5
                    )
                    status_badge.pack(side="right", ipadx=10, ipady=5)
                    
                    # Details grid
                    details_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    details_frame.pack(fill="x", pady=(0, 10))
                    
                    # Left column
                    left_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                    left_col.pack(side="left", fill="both", expand=True)
                    
                    ctk.CTkLabel(
                        left_col,
                        text=f"🆔 Apartment ID: {apt.get('apartment_ID', 'N/A')}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(
                        left_col,
                        text=f"🛏️ Bedrooms: {apt.get('number_of_beds', 'N/A')}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
                    
                    # Right column
                    right_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                    right_col.pack(side="right", fill="both", expand=True)
                    
                    ctk.CTkLabel(
                        right_col,
                        text=f"📍 Location: {apt.get('city', 'N/A')}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(
                        right_col,
                        text=f"💰 Monthly Rent: £{apt.get('monthly_rent', 'N/A')}",
                        font=("Arial", 12),
                        anchor="w"
                    ).pack(fill="x", pady=2)
            
            def perform_apartment_search():
                """Execute apartment search with filters"""
                # Get all apartments
                all_apartments = apt_repo.get_all_apartments()
                
                # Apply filters
                filtered = all_apartments
                
                # Location filter
                location_filter = filters['location'].get()
                if location_filter != 'All':
                    filtered = [a for a in filtered if a['city'] == location_filter]
                
                # Beds filter
                beds_filter = filters['beds'].get()
                if beds_filter != 'Any':
                    if beds_filter == '5+':
                        filtered = [a for a in filtered if a['number_of_beds'] >= 5]
                    else:
                        filtered = [a for a in filtered if a['number_of_beds'] == int(beds_filter)]
                
                # Status filter
                status_filter = filters['status'].get()
                if status_filter != 'All':
                    filtered = [a for a in filtered if a['status'] == status_filter]
                
                # Price filter
                max_rent = filters['max_rent'].get().strip()
                if max_rent and max_rent.isdigit():
                    filtered = [a for a in filtered if a['monthly_rent'] <= int(max_rent)]
                
                display_apartment_results(filtered)
            
            # Show initial message
            initial_msg = ctk.CTkLabel(
                results_frame,
                text="👆 Set your filters and click Search to find apartments",
                font=("Arial", 14),
                text_color=("gray50", "gray60")
            )
            initial_msg.pack(pady=40)
        
        search_apt_button.configure(command=setup_apartment_search_popup)

    def load_maintenance_content(self, row):
        maintenance_card = pe.function_card(row, "Maintenance Requests", side="left")
        
        # Register maintenance request button with popup
        maint_button, maint_popup_func = pe.popup_card(
            maintenance_card,
            button_text="Register Request",
            title="Register Maintenance Request",
            small=False,
            button_size="large"
        )
        
        def setup_maint_popup():
            from datetime import datetime
            content = maint_popup_func()
            
            scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
            scrollable.pack(fill="both", expand=True, padx=30, pady=20)
            
            entries = {}
            
            # === TENANT & PROPERTY SECTION ===
            section_label = ctk.CTkLabel(
                scrollable, 
                text="━━━━━━━━━━━━ Tenant & Property Details ━━━━━━━━━━━━", 
                font=("Arial", 14, "bold"),
                text_color=("#1a3c5c", "#4196E0")
            )
            section_label.pack(fill="x", pady=(0, 15))
            
            # Tenant ID
            tenant_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            tenant_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(tenant_frame, text="Tenant ID *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['tenant_id'] = ctk.CTkEntry(tenant_frame, height=40, font=("Arial", 14), placeholder_text="Enter tenant ID number")
            entries['tenant_id'].pack(fill="x")
            
            # Apartment ID
            apt_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            apt_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(apt_frame, text="Apartment ID *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['apartment_id'] = ctk.CTkEntry(apt_frame, height=40, font=("Arial", 14), placeholder_text="Enter apartment ID number")
            entries['apartment_id'].pack(fill="x")
            
            # === ISSUE DETAILS SECTION ===
            section_label2 = ctk.CTkLabel(
                scrollable, 
                text="━━━━━━━━━━━━ Issue Details ━━━━━━━━━━━━", 
                font=("Arial", 14, "bold"),
                text_color=("#1a3c5c", "#4196E0")
            )
            section_label2.pack(fill="x", pady=(15, 15))
            
            # Issue Description
            issue_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            issue_frame.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(issue_frame, text="Issue Description *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
            entries['issue_description'] = ctk.CTkTextbox(issue_frame, height=120, font=("Arial", 14))
            entries['issue_description'].insert("1.0", "Describe the maintenance issue in detail...")
            entries['issue_description'].bind("<FocusIn>", lambda e: entries['issue_description'].delete("1.0", "end") if entries['issue_description'].get("1.0", "end").strip() == "Describe the maintenance issue in detail..." else None)
            entries['issue_description'].pack(fill="x")
            
            # Priority Level
            priority_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            priority_frame.pack(fill="x", pady=(12, 0))
            ctk.CTkLabel(priority_frame, text="Priority Level *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 10))
            
            priority_var = ctk.StringVar(value="2")
            priority_options = ctk.CTkFrame(priority_frame, fg_color=("gray90", "gray17"), corner_radius=8)
            priority_options.pack(fill="x", pady=(0, 0))
            
            priority_buttons = []
            for level, label, color in [("3", "🔴 High Priority", "#C41E3A"), ("2", "🟡 Medium Priority", "#FFA500"), ("1", "🟢 Low Priority", "#2D862D")]:
                btn = ctk.CTkRadioButton(
                    priority_options,
                    text=label,
                    variable=priority_var,
                    value=level,
                    font=("Arial", 14, "bold"),
                    fg_color=("#1a3c5c", "#4196E0"),
                    hover_color=("#0d2438", "#3380CC")
                )
                btn.pack(side="left", padx=20, pady=15, expand=True)
                priority_buttons.append(btn)
            
            entries['priority_level'] = priority_var
            
            # Status messages
            status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            status_frame.pack(fill="x", pady=(15, 0))
            
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
                
                issue_text = entries['issue_description'].get("1.0", "end").strip()
                if not issue_text or issue_text == "Describe the maintenance issue in detail...":
                    error_label.configure(text="❌ Error: Issue description is required")
                    error_label.pack(pady=10)
                    return
                
                # Submit
                values = {
                    'tenant_id': int(entries['tenant_id'].get().strip()),
                    'apartment_id': int(entries['apartment_id'].get().strip()),
                    'issue_description': issue_text,
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
                    entries['issue_description'].insert("1.0", "Describe the maintenance issue in detail...")
                    entries['priority_level'].set("2")
                else:
                    error_label.configure(text=f"❌ {str(result)}")
                    error_label.pack(pady=10)
            
            submit_btn = ctk.CTkButton(
                scrollable,
                text="📝 Submit Maintenance Request",
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
            button_size="large"
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
                    # Summary header
                    summary_frame = ctk.CTkFrame(scrollable, fg_color=("gray95", "gray15"), corner_radius=10)
                    summary_frame.pack(fill="x", pady=(0, 15))
                    
                    pending_count = sum(1 for r in requests if not r.get('completed'))
                    completed_count = sum(1 for r in requests if r.get('completed'))
                    
                    summary_text = f"📊 Total Requests: {len(requests)}  |  ⏳ Pending: {pending_count}  |  ✓ Completed: {completed_count}"
                    ctk.CTkLabel(
                        summary_frame,
                        text=summary_text,
                        font=("Arial", 14, "bold"),
                        text_color=("#1a3c5c", "#4196E0")
                    ).pack(pady=15)
                    
                    for req in requests:
                        req_frame = ctk.CTkFrame(scrollable, fg_color=("gray90", "gray17"), corner_radius=10)
                        req_frame.pack(fill="x", pady=(0, 12))
                        
                        # Header with status badge
                        header_frame = ctk.CTkFrame(req_frame, fg_color="transparent")
                        header_frame.pack(fill="x", padx=20, pady=(15, 10))
                        
                        is_completed = req.get('completed')
                        status_text = "✅ COMPLETED" if is_completed else "🚧 PENDING"
                        status_color = ("#2D862D", "#4CAF50") if is_completed else ("#FFA500", "#FFB347")
                        
                        # Request ID and Status
                        id_status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
                        id_status_frame.pack(fill="x")
                        
                        ctk.CTkLabel(
                            id_status_frame,
                            text=f"Request #{req.get('request_ID', 'N/A')}",
                            font=("Arial", 16, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                            anchor="w"
                        ).pack(side="left")
                        
                        status_badge = ctk.CTkLabel(
                            id_status_frame,
                            text=status_text,
                            font=("Arial", 11, "bold"),
                            text_color="white",
                            fg_color=status_color,
                            corner_radius=5
                        )
                        status_badge.pack(side="right", padx=5, ipadx=10, ipady=5)
                        
                        # Priority badge
                        priority = req.get('priority_level', 2)
                        if priority == 3:
                            priority_text = "🔴 HIGH"
                            priority_color = ("#C41E3A", "#FF6B6B")
                        elif priority == 2:
                            priority_text = "🟡 MEDIUM"
                            priority_color = ("#FFA500", "#FFB347")
                        else:
                            priority_text = "🟢 LOW"
                            priority_color = ("#2D862D", "#4CAF50")
                        
                        priority_badge = ctk.CTkLabel(
                            id_status_frame,
                            text=priority_text,
                            font=("Arial", 11, "bold"),
                            text_color="white",
                            fg_color=priority_color,
                            corner_radius=5
                        )
                        priority_badge.pack(side="right", ipadx=10, ipady=5)
                        
                        # Details section
                        details_frame = ctk.CTkFrame(req_frame, fg_color="transparent")
                        details_frame.pack(fill="x", padx=20, pady=(5, 10))
                        
                        # Left column
                        left_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                        left_col.pack(side="left", fill="both", expand=True)
                        
                        ctk.CTkLabel(
                            left_col,
                            text=f"👤 Tenant: {req.get('tenant_name', 'N/A')}",
                            font=("Arial", 12),
                            anchor="w"
                        ).pack(fill="x", pady=2)
                        
                        ctk.CTkLabel(
                            left_col,
                            text=f"🏠 Apartment: {req.get('apartment_address', 'N/A')}",
                            font=("Arial", 12),
                            anchor="w"
                        ).pack(fill="x", pady=2)
                        
                        # Right column
                        right_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                        right_col.pack(side="right", fill="both", expand=True)
                        
                        ctk.CTkLabel(
                            right_col,
                            text=f"📅 Reported: {req.get('reported_date', 'N/A')}",
                            font=("Arial", 12),
                            anchor="w"
                        ).pack(fill="x", pady=2)
                        
                        # Issue description
                        issue_frame = ctk.CTkFrame(req_frame, fg_color=("gray85", "gray20"), corner_radius=5)
                        issue_frame.pack(fill="x", padx=20, pady=(0, 10))
                        
                        ctk.CTkLabel(
                            issue_frame,
                            text=f"📋 Issue: {req.get('issue_description', 'N/A')}",
                            font=("Arial", 12),
                            justify="left",
                            anchor="w",
                            wraplength=600
                        ).pack(padx=12, pady=10, fill="x")
                        
                        # Button container
                        button_frame = ctk.CTkFrame(req_frame, fg_color="transparent")
                        button_frame.pack(fill="x", padx=20, pady=(0, 15))
                        
                        request_id = req.get('request_ID')
                        
                        # Flag/Unflag button
                        flag_text = "↩️ Mark as Pending" if is_completed else "✅ Mark as Completed"
                        flag_btn = ctk.CTkButton(
                            button_frame,
                            text=flag_text,
                            command=lambda rid=request_id, completed=is_completed: handle_flag_request(rid, completed),
                            height=38,
                            font=("Arial", 13, "bold"),
                            fg_color=("#4196E0", "#3380CC") if not is_completed else ("#FFA500", "#FF8C00"),
                            hover_color=("#3380CC", "#2570B8") if not is_completed else ("#FF8C00", "#E67E00"),
                            width=200
                        )
                        flag_btn.pack(side="left", padx=(0, 10))
                        
                        # Delete button
                        delete_btn = ctk.CTkButton(
                            button_frame,
                            text="🗑️ Delete",
                            command=lambda rid=request_id: handle_delete_request(rid),
                            height=38,
                            font=("Arial", 13, "bold"),
                            fg_color=("#C41E3A", "#FF6B6B"),
                            hover_color=("#A01828", "#E65A5A"),
                            width=130
                        )
                        delete_btn.pack(side="left")
                else:
                    ctk.CTkLabel(
                        scrollable,
                        text="📭 No maintenance requests found",
                        font=("Arial", 15),
                        text_color=("gray50", "gray60")
                    ).pack(pady=40)
            
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
            small=False,
            button_size="medium"
        )
        
        def setup_complaint_popup():
            from datetime import datetime
            content = complaint_popup_func()
            
            scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
            scrollable.pack(fill="both", expand=True, padx=30, pady=20)
            
            entries = {}
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 📋 TENANT INFORMATION
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            section_label = ctk.CTkLabel(
                scrollable,
                text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📋 TENANT INFORMATION\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                font=("Arial", 14, "bold"),
                text_color=("#1a3c5c", "#4196E0"),
                justify="center"
            )
            section_label.pack(fill="x", pady=(0, 15))
            
            # Tenant ID
            tenant_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            tenant_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(
                tenant_frame, 
                text="👤 Tenant ID *", 
                font=("Arial", 13, "bold"), 
                text_color=("#1a3c5c", "#4196E0")
            ).pack(anchor="w", pady=(0, 5))
            entries['tenant_id'] = ctk.CTkEntry(
                tenant_frame, 
                height=40, 
                font=("Arial", 14),
                placeholder_text="Enter tenant ID number"
            )
            entries['tenant_id'].pack(fill="x")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 💬 COMPLAINT DETAILS
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            section_label2 = ctk.CTkLabel(
                scrollable,
                text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💬 COMPLAINT DETAILS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                font=("Arial", 14, "bold"),
                text_color=("#1a3c5c", "#4196E0"),
                justify="center"
            )
            section_label2.pack(fill="x", pady=(20, 15))
            
            # Complaint Description
            desc_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            desc_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(
                desc_frame, 
                text="📝 Complaint Description *", 
                font=("Arial", 13, "bold"), 
                text_color=("#1a3c5c", "#4196E0")
            ).pack(anchor="w", pady=(0, 5))
            
            ctk.CTkLabel(
                desc_frame,
                text="Please provide detailed information about the complaint",
                font=("Arial", 10),
                text_color=("gray50", "gray60")
            ).pack(anchor="w", pady=(0, 8))
            
            entries['description'] = ctk.CTkTextbox(
                desc_frame, 
                height=180, 
                font=("Arial", 14),
                wrap="word"
            )
            entries['description'].pack(fill="x")
            
            # Status messages
            status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            status_frame.pack(fill="x", pady=(15, 0))
            
            error_label = ctk.CTkLabel(
                status_frame, 
                text="", 
                font=("Arial", 13, "bold"), 
                text_color=("#C41E3A", "#FF6B6B")
            )
            success_label = ctk.CTkLabel(
                status_frame, 
                text="", 
                font=("Arial", 13, "bold"), 
                text_color=("#2D862D", "#4CAF50")
            )
            
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
                    success_label.configure(text="✅ Complaint registered successfully!")
                    success_label.pack(pady=10)
                    entries['tenant_id'].delete(0, 'end')
                    entries['description'].delete("1.0", "end")
                else:
                    error_label.configure(text=f"❌ {str(result)}")
                    error_label.pack(pady=10)
            
            # Submit button
            submit_btn = ctk.CTkButton(
                scrollable,
                text="📝 Register Complaint",
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
                    # Summary header
                    summary_frame = ctk.CTkFrame(scrollable, fg_color=("gray95", "gray15"), corner_radius=10)
                    summary_frame.pack(fill="x", pady=(0, 15))
                    
                    pending_count = sum(1 for c in complaints if not c.get('resolved'))
                    resolved_count = sum(1 for c in complaints if c.get('resolved'))
                    
                    summary_text = f"💬 Total Complaints: {len(complaints)}  |  🚧 Pending: {pending_count}  |  ✅ Resolved: {resolved_count}"
                    ctk.CTkLabel(
                        summary_frame,
                        text=summary_text,
                        font=("Arial", 14, "bold"),
                        text_color=("#1a3c5c", "#4196E0")
                    ).pack(pady=15)
                    
                    for comp in complaints:
                        comp_frame = ctk.CTkFrame(scrollable, fg_color=("gray90", "gray17"), corner_radius=10)
                        comp_frame.pack(fill="x", pady=(0, 12))
                        
                        # Header with status badge
                        header_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
                        header_frame.pack(fill="x", padx=20, pady=(15, 10))
                        
                        is_resolved = comp.get('resolved')
                        status_text = "✅ RESOLVED" if is_resolved else "🚧 PENDING"
                        status_color = ("#2D862D", "#4CAF50") if is_resolved else ("#FFA500", "#FFB347")
                        
                        # Complaint ID and Status
                        id_status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
                        id_status_frame.pack(fill="x")
                        
                        ctk.CTkLabel(
                            id_status_frame,
                            text=f"Complaint #{comp.get('complaint_ID', 'N/A')}",
                            font=("Arial", 16, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                            anchor="w"
                        ).pack(side="left")
                        
                        status_badge = ctk.CTkLabel(
                            id_status_frame,
                            text=status_text,
                            font=("Arial", 11, "bold"),
                            text_color="white",
                            fg_color=status_color,
                            corner_radius=5
                        )
                        status_badge.pack(side="right", ipadx=10, ipady=5)
                        
                        # Details section
                        details_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
                        details_frame.pack(fill="x", padx=20, pady=(5, 10))
                        
                        # Tenant info
                        ctk.CTkLabel(
                            details_frame,
                            text=f"👤 Tenant: {comp.get('tenant_name', 'N/A')}",
                            font=("Arial", 12),
                            anchor="w"
                        ).pack(fill="x", pady=2)
                        
                        # Date submitted
                        ctk.CTkLabel(
                            details_frame,
                            text=f"📅 Submitted: {comp.get('date_submitted', 'N/A')}",
                            font=("Arial", 12),
                            anchor="w"
                        ).pack(fill="x", pady=2)
                        
                        # Description section
                        desc_section = ctk.CTkFrame(comp_frame, fg_color="transparent")
                        desc_section.pack(fill="x", padx=20, pady=(5, 10))
                        
                        ctk.CTkLabel(
                            desc_section,
                            text="📝 Description:",
                            font=("Arial", 12, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                            anchor="w"
                        ).pack(fill="x", pady=(0, 5))
                        
                        desc_box = ctk.CTkTextbox(
                            desc_section,
                            height=80,
                            font=("Arial", 12),
                            fg_color=("gray85", "gray25"),
                            wrap="word"
                        )
                        desc_box.pack(fill="x")
                        desc_box.insert("1.0", comp.get('description', 'N/A'))
                        desc_box.configure(state="disabled")
                        
                        # Button container
                        button_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
                        button_frame.pack(fill="x", padx=20, pady=(5, 15))
                        
                        complaint_id = comp.get('complaint_ID')
                        
                        # Flag/Unflag button
                        flag_text = "↩️ Mark as Pending" if is_resolved else "✅ Mark as Resolved"
                        flag_btn = ctk.CTkButton(
                            button_frame,
                            text=flag_text,
                            command=lambda cid=complaint_id, resolved=is_resolved: handle_flag_complaint(cid, resolved),
                            height=38,
                            font=("Arial", 13, "bold"),
                            fg_color=("#4196E0", "#3380CC") if not is_resolved else ("#FFA500", "#FF8C00"),
                            hover_color=("#3380CC", "#2570B8") if not is_resolved else ("#FF8C00", "#E67E00"),
                            width=200
                        )
                        flag_btn.pack(side="left", padx=(0, 10))
                        
                        # Delete button
                        delete_btn = ctk.CTkButton(
                            button_frame,
                            text="🗑️ Delete",
                            command=lambda cid=complaint_id: handle_delete_complaint(cid),
                            height=38,
                            font=("Arial", 13, "bold"),
                            fg_color=("#C41E3A", "#FF6B6B"),
                            hover_color=("#A01828", "#E65A5A"),
                            width=130
                        )
                        delete_btn.pack(side="left")
                else:
                    ctk.CTkLabel(
                        scrollable,
                        text="💬 No complaints found",
                        font=("Arial", 15),
                        text_color=("gray50", "gray60")
                    ).pack(pady=40)
            
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

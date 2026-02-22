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
        """Register a new tenant with their details."""
        first_name = values.get("First Name", "")
        last_name = values.get("Last Name", "")
        dob = values.get("Date of Birth", "")
        ni_number = values.get("NI Number", "")
        email = values.get("Email", "")
        phone = values.get("Phone", "")
        occupation = values.get("Occupation", "")
        annual_salary = values.get("Annual Salary", 0)
        right_to_rent = values.get("Right to Rent", "N")
        credit_check = values.get("Credit Check", "Pending")
        pets = values.get("Pets", "N")

        try:
            tenant_repo.create_tenant(
                first_name,
                last_name,
                dob,
                ni_number,
                email,
                phone,
                occupation,
                annual_salary,
                right_to_rent,
                credit_check,
                pets,
            )
            return True  # Success
        except Exception as e:
            return f"Failed to register tenant: {str(e)}"

    def get_tenant_info(self, tenant_id: int):
        """Retrieve information for a specific tenant."""
        print(f"Getting info for tenant ID: {tenant_id}")

    def register_maintenance_request(self, tenant_id: int, request_details: str):
        """Register a maintenance request for a tenant."""
        print(
            f"Registering maintenance request for tenant ID: {tenant_id} with details: {request_details}"
        )

    def register_complaint(self, tenant_id: int, complaint_details: str):
        """Register a complaint from a tenant."""
        print(
            f"Registering complaint for tenant ID: {tenant_id} with details: {complaint_details}"
        )

    # ============================= ^ Front Desk functions ^ =====================================

    # ============================= v Homepage UI Content v =====================================
    def load_homepage_content(self, home_page):
        """Load Front Desk Staff-specific homepage content."""
        # Load base content first
        super().load_homepage_content(home_page)

        row1 = pe.row_container(parent=home_page)

        # Tenant Management Card
        self.load_tenant_content(row1)

        # Maintenance Requests Card
        self.load_maintenance_content(row1)

        # Complaints Management Card
        self.load_complaints_content(row1)

    def load_tenant_content(self, row):
        tenant_card = pe.function_card(row, "Tenant Management", side="left")

        # Create popup button and setup function
        button, open_popup_func = pe.popup_card(
            tenant_card,
            button_text="Register Tenant",
            title="Register New Tenant",
            small=False,
            button_size="medium",
        )

        def setup_popup():
            content = open_popup_func()

            # Auto-format date helper
            def auto_format_date(entry_widget):
                def on_change(*args):
                    current = entry_widget.get().replace("-", "")
                    current = "".join(filter(str.isdigit, current))[:8]
                    formatted = current
                    if len(current) > 4:
                        formatted = current[:4] + "-" + current[4:]
                    if len(current) > 6:
                        formatted = formatted[:7] + "-" + formatted[7:]
                    if entry_widget.get() != formatted:
                        entry_widget.delete(0, "end")
                        entry_widget.insert(0, formatted)

                entry_widget.bind("<KeyRelease>", on_change)

            # Auto-format salary helper
            def auto_format_salary(entry_widget):
                def on_change(*args):
                    current = entry_widget.get().replace(",", "").replace("£", "")
                    if current and not current.replace(".", "", 1).isdigit():
                        current = "".join(
                            filter(lambda x: x.isdigit() or x == ".", current)
                        )
                    if entry_widget.get() != current:
                        entry_widget.delete(0, "end")
                        entry_widget.insert(0, current)

                entry_widget.bind("<KeyRelease>", on_change)

            # Create scrollable container for the form
            scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
            scrollable.pack(fill="both", expand=True, padx=30, pady=20)

            # Store entry widgets
            entries = {}

            # BRANDING: Paragon Apartments Header
            brand_frame = ctk.CTkFrame(
                scrollable,
                fg_color=("#1a5c37", "#0d3d24"),
                corner_radius=12,
                border_width=3,
                border_color=("#d4af37", "#b8941f"),
            )
            brand_frame.pack(fill="x", pady=(0, 25))

            brand_content = ctk.CTkFrame(brand_frame, fg_color="transparent")
            brand_content.pack(fill="x", padx=25, pady=20)

            ctk.CTkLabel(
                brand_content,
                text="PARAGON APARTMENTS",
                font=("Arial", 32, "bold"),
                text_color=("#d4af37", "#d4af37"),
            ).pack(anchor="w")

            ctk.CTkLabel(
                brand_content,
                text="Premium Property Management",
                font=("Arial", 14),
                text_color=("#ffffff", "#e0e0e0"),
            ).pack(anchor="w", pady=(2, 8))

            ctk.CTkFrame(brand_content, height=2, fg_color=("#d4af37", "#b8941f")).pack(
                fill="x", pady=(0, 8)
            )

            ctk.CTkLabel(
                brand_content,
                text="New Tenant Registration Form",
                font=("Arial", 20, "bold"),
                text_color=("#ffffff", "#ffffff"),
            ).pack(anchor="w")

            ctk.CTkLabel(
                brand_content,
                text="Please complete all required fields marked with an asterisk (*)",
                font=("Arial", 12),
                text_color=("#e0e0e0", "#c0c0c0"),
            ).pack(anchor="w", pady=(3, 0))

            # SECTION 1: Personal Information
            section1 = ctk.CTkFrame(
                scrollable,
                fg_color=("gray85", "gray20"),
                corner_radius=10,
                border_width=2,
                border_color=("#1a5c37", "#0d3d24"),
            )
            section1.pack(fill="x", pady=(0, 20))

            ctk.CTkLabel(
                section1,
                text="📋 Personal Information",
                font=("Arial", 18, "bold"),
                text_color=("#1a5c37", "#5FB041"),
                anchor="w",
            ).pack(fill="x", padx=20, pady=(15, 10))

            # Grid container for 2 columns
            grid1 = ctk.CTkFrame(section1, fg_color="transparent")
            grid1.pack(fill="x", padx=20, pady=(0, 15))
            grid1.grid_columnconfigure(0, weight=1)
            grid1.grid_columnconfigure(1, weight=1)

            # First Name
            fname_frame = ctk.CTkFrame(grid1, fg_color="transparent")
            fname_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                fname_frame,
                text="First Name *",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 5))
            entries["First Name"] = ctk.CTkEntry(
                fname_frame,
                height=40,
                font=("Arial", 14),
                border_width=2,
                border_color=("#1a5c37", "#5FB041"),
            )
            entries["First Name"].pack(fill="x")

            # Last Name
            lname_frame = ctk.CTkFrame(grid1, fg_color="transparent")
            lname_frame.grid(row=0, column=1, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                lname_frame,
                text="Last Name *",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 5))
            entries["Last Name"] = ctk.CTkEntry(
                lname_frame,
                height=40,
                font=("Arial", 14),
                border_width=2,
                border_color=("#1a5c37", "#5FB041"),
            )
            entries["Last Name"].pack(fill="x")

            # Date of Birth
            dob_frame = ctk.CTkFrame(grid1, fg_color="transparent")
            dob_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                dob_frame,
                text="Date of Birth *(YYYY-MM-DD)",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 5))
            entries["Date of Birth"] = ctk.CTkEntry(
                dob_frame,
                placeholder_text="YYYY-MM-DD",
                height=40,
                font=("Arial", 14),
                border_width=2,
                border_color=("#1a5c37", "#5FB041"),
            )
            entries["Date of Birth"].pack(fill="x")
            auto_format_date(entries["Date of Birth"])

            # NI Number
            ni_frame = ctk.CTkFrame(grid1, fg_color="transparent")
            ni_frame.grid(row=1, column=1, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                ni_frame,
                text="National Insurance Number *",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 5))
            entries["NI Number"] = ctk.CTkEntry(
                ni_frame,
                placeholder_text="AB123456C",
                height=40,
                font=("Arial", 14),
                border_width=2,
                border_color=("#1a5c37", "#5FB041"),
            )
            entries["NI Number"].pack(fill="x")

            # SECTION 2: Contact Information
            section2 = ctk.CTkFrame(
                scrollable,
                fg_color=("gray85", "gray20"),
                corner_radius=10,
                border_width=2,
                border_color=("#1a5c37", "#0d3d24"),
            )
            section2.pack(fill="x", pady=(0, 20))

            ctk.CTkLabel(
                section2,
                text="📞 Contact Information",
                font=("Arial", 18, "bold"),
                text_color=("#1a5c37", "#5FB041"),
                anchor="w",
            ).pack(fill="x", padx=20, pady=(15, 10))

            grid2 = ctk.CTkFrame(section2, fg_color="transparent")
            grid2.pack(fill="x", padx=20, pady=(0, 15))
            grid2.grid_columnconfigure(0, weight=1)
            grid2.grid_columnconfigure(1, weight=1)

            # Email
            email_frame = ctk.CTkFrame(grid2, fg_color="transparent")
            email_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                email_frame,
                text="Email Address *",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 5))
            entries["Email"] = ctk.CTkEntry(
                email_frame,
                placeholder_text="example@email.com",
                height=40,
                font=("Arial", 14),
                border_width=2,
                border_color=("#1a5c37", "#5FB041"),
            )
            entries["Email"].pack(fill="x")

            # Phone
            phone_frame = ctk.CTkFrame(grid2, fg_color="transparent")
            phone_frame.grid(row=0, column=1, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                phone_frame,
                text="Phone Number *",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 5))
            entries["Phone"] = ctk.CTkEntry(
                phone_frame,
                placeholder_text="07123456789",
                height=40,
                font=("Arial", 14),
                border_width=2,
                border_color=("#1a5c37", "#5FB041"),
            )
            entries["Phone"].pack(fill="x")

            # SECTION 3: Employment Information
            section3 = ctk.CTkFrame(
                scrollable,
                fg_color=("gray85", "gray20"),
                corner_radius=10,
                border_width=2,
                border_color=("#1a5c37", "#0d3d24"),
            )
            section3.pack(fill="x", pady=(0, 20))

            ctk.CTkLabel(
                section3,
                text="💼 Employment Information",
                font=("Arial", 18, "bold"),
                text_color=("#1a5c37", "#5FB041"),
                anchor="w",
            ).pack(fill="x", padx=20, pady=(15, 10))

            grid3 = ctk.CTkFrame(section3, fg_color="transparent")
            grid3.pack(fill="x", padx=20, pady=(0, 15))
            grid3.grid_columnconfigure(0, weight=1)
            grid3.grid_columnconfigure(1, weight=1)

            # Occupation
            occ_frame = ctk.CTkFrame(grid3, fg_color="transparent")
            occ_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                occ_frame,
                text="Occupation *",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 5))
            entries["Occupation"] = ctk.CTkEntry(
                occ_frame,
                placeholder_text="Job Title",
                height=40,
                font=("Arial", 14),
                border_width=2,
                border_color=("#1a5c37", "#5FB041"),
            )
            entries["Occupation"].pack(fill="x")

            # Annual Salary
            salary_frame = ctk.CTkFrame(grid3, fg_color="transparent")
            salary_frame.grid(row=0, column=1, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                salary_frame,
                text="Annual Salary (£) *",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 5))
            entries["Annual Salary"] = ctk.CTkEntry(
                salary_frame,
                placeholder_text="35000",
                height=40,
                font=("Arial", 14),
                border_width=2,
                border_color=("#1a5c37", "#5FB041"),
            )
            entries["Annual Salary"].pack(fill="x")
            auto_format_salary(entries["Annual Salary"])

            # SECTION 4: Verification & Additional
            section4 = ctk.CTkFrame(
                scrollable,
                fg_color=("gray85", "gray20"),
                corner_radius=10,
                border_width=2,
                border_color=("#1a5c37", "#0d3d24"),
            )
            section4.pack(fill="x", pady=(0, 20))

            ctk.CTkLabel(
                section4,
                text="✓ Verification & Additional Details",
                font=("Arial", 18, "bold"),
                text_color=("#1a5c37", "#5FB041"),
                anchor="w",
            ).pack(fill="x", padx=20, pady=(15, 10))

            grid4 = ctk.CTkFrame(section4, fg_color="transparent")
            grid4.pack(fill="x", padx=20, pady=(0, 15))
            grid4.grid_columnconfigure(0, weight=1)

            # Right to Rent - Radio buttons
            rent_frame = ctk.CTkFrame(grid4, fg_color="transparent")
            rent_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                rent_frame,
                text="Right to Rent *",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 8))

            rent_var = ctk.StringVar(value="Y")
            rent_options = ctk.CTkFrame(rent_frame, fg_color="transparent")
            rent_options.pack(fill="x")

            ctk.CTkRadioButton(
                rent_options,
                text="Yes",
                variable=rent_var,
                value="Y",
                font=("Arial", 13),
                radiobutton_width=20,
                radiobutton_height=20,
                fg_color=("#1a5c37", "#5FB041"),
                hover_color=("#0d3d24", "#4A9033"),
            ).pack(side="left", padx=(0, 20))

            ctk.CTkRadioButton(
                rent_options,
                text="No",
                variable=rent_var,
                value="N",
                font=("Arial", 13),
                radiobutton_width=20,
                radiobutton_height=20,
                fg_color=("#1a5c37", "#5FB041"),
                hover_color=("#0d3d24", "#4A9033"),
            ).pack(side="left")

            entries["Right to Rent"] = rent_var

            # Credit Check - Radio buttons
            credit_frame = ctk.CTkFrame(grid4, fg_color="transparent")
            credit_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                credit_frame,
                text="Credit Check Status *",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 8))

            credit_var = ctk.StringVar(value="Pending")
            credit_options = ctk.CTkFrame(credit_frame, fg_color="transparent")
            credit_options.pack(fill="x")

            ctk.CTkRadioButton(
                credit_options,
                text="Passed",
                variable=credit_var,
                value="Passed",
                font=("Arial", 13),
                radiobutton_width=20,
                radiobutton_height=20,
                fg_color=("#1a5c37", "#5FB041"),
                hover_color=("#0d3d24", "#4A9033"),
            ).pack(side="left", padx=(0, 20))

            ctk.CTkRadioButton(
                credit_options,
                text="Pending",
                variable=credit_var,
                value="Pending",
                font=("Arial", 13),
                radiobutton_width=20,
                radiobutton_height=20,
                fg_color=("#1a5c37", "#5FB041"),
                hover_color=("#0d3d24", "#4A9033"),
            ).pack(side="left", padx=(0, 20))

            ctk.CTkRadioButton(
                credit_options,
                text="Failed",
                variable=credit_var,
                value="Failed",
                font=("Arial", 13),
                radiobutton_width=20,
                radiobutton_height=20,
                fg_color=("#1a5c37", "#5FB041"),
                hover_color=("#0d3d24", "#4A9033"),
            ).pack(side="left")

            entries["Credit Check"] = credit_var

            # Pets - Radio buttons
            pets_frame = ctk.CTkFrame(grid4, fg_color="transparent")
            pets_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15), padx=5)
            ctk.CTkLabel(
                pets_frame,
                text="Pets",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
            ).pack(anchor="w", pady=(0, 8))

            pets_var = ctk.StringVar(value="N")
            pets_options = ctk.CTkFrame(pets_frame, fg_color="transparent")
            pets_options.pack(fill="x")

            ctk.CTkRadioButton(
                pets_options,
                text="No",
                variable=pets_var,
                value="N",
                font=("Arial", 13),
                radiobutton_width=20,
                radiobutton_height=20,
                fg_color=("#1a5c37", "#5FB041"),
                hover_color=("#0d3d24", "#4A9033"),
            ).pack(side="left", padx=(0, 20))

            ctk.CTkRadioButton(
                pets_options,
                text="Yes",
                variable=pets_var,
                value="Y",
                font=("Arial", 13),
                radiobutton_width=20,
                radiobutton_height=20,
                fg_color=("#1a5c37", "#5FB041"),
                hover_color=("#0d3d24", "#4A9033"),
            ).pack(side="left")

            entries["Pets"] = pets_var

            # Status messages
            status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            status_frame.pack(fill="x", pady=(10, 0))

            error_label = ctk.CTkLabel(
                status_frame,
                text="",
                font=("Arial", 13, "bold"),
                text_color=("#C41E3A", "#FF6B6B"),
                wraplength=800,
            )
            success_label = ctk.CTkLabel(
                status_frame,
                text="",
                font=("Arial", 13, "bold"),
                text_color=("#1a5c37", "#5FB041"),
                wraplength=800,
            )

            # Submit button section
            button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            button_frame.pack(fill="x", pady=(20, 10))

            def handle_submit():
                error_label.pack_forget()
                success_label.pack_forget()

                # Validation
                required_fields = [
                    "First Name",
                    "Last Name",
                    "Date of Birth",
                    "NI Number",
                    "Email",
                    "Phone",
                    "Occupation",
                    "Annual Salary",
                ]
                for field in required_fields:
                    if not entries[field].get().strip():
                        error_label.configure(text=f"❌ Error: {field} is required")
                        error_label.pack(pady=10)
                        return

                # Validate using input_validation functions
                validations = [
                    (
                        input_validation.is_email_valid(entries["Email"].get().strip()),
                        "Invalid email format",
                    ),
                    (
                        input_validation.is_phone_valid(entries["Phone"].get().strip()),
                        "Invalid phone number format",
                    ),
                    (
                        input_validation.is_annual_salary_valid(
                            entries["Annual Salary"].get().strip()
                        ),
                        "Annual Salary must be a valid positive number",
                    ),
                    (
                        input_validation.is_date_of_birth_valid(
                            entries["Date of Birth"].get().strip()
                        ),
                        "Date of Birth must be in YYYY-MM-DD format and over 18 years old",
                    ),
                    (
                        input_validation.is_NI_number_valid(
                            entries["NI Number"].get().strip()
                        ),
                        "Invalid National Insurance Number format",
                    ),
                ]

                for is_valid, error_msg in validations:
                    if not is_valid:
                        error_label.configure(text=f"❌ Error: {error_msg}")
                        error_label.pack(pady=10)
                        return

                # Collect values
                values = {}
                for key, widget in entries.items():
                    if isinstance(widget, ctk.CTkEntry):
                        values[key] = widget.get().strip()
                    else:  # StringVar from radio buttons
                        values[key] = widget.get()

                # Submit
                result = self.register_tenant(values)
                if result is True:
                    success_label.configure(
                        text="✓ Tenant registered successfully with Paragon Apartments!"
                    )
                    success_label.pack(pady=10)
                    # Clear fields
                    for key, widget in entries.items():
                        if isinstance(widget, ctk.CTkEntry):
                            widget.delete(0, "end")
                        elif key == "Right to Rent":
                            widget.set("Y")
                        elif key == "Credit Check":
                            widget.set("Pending")
                        elif key == "Pets":
                            widget.set("N")
                else:
                    error_label.configure(text=f"❌ {str(result)}")
                    error_label.pack(pady=10)

            submit_btn = ctk.CTkButton(
                button_frame,
                text="Register Tenant with Paragon Apartments",
                command=handle_submit,
                height=55,
                font=("Arial", 18, "bold"),
                fg_color=("#1a5c37", "#5FB041"),
                hover_color=("#0d3d24", "#4A9033"),
                corner_radius=10,
                border_width=2,
                border_color=("#d4af37", "#b8941f"),
            )
            submit_btn.pack(fill="x", pady=(0, 10))

        button.configure(command=setup_popup)

        pe.action_button(
            tenant_card, text="Get Tenant Info", command=lambda: self.get_tenant_info(1)
        )

    def load_maintenance_content(self, row):
        maintenance_card = pe.function_card(row, "Maintenance Requests", side="left")

        pe.action_button(
            maintenance_card,
            text="Register Request",
            command=lambda: self.register_maintenance_request(1, "Broken faucet"),
        )

        pe.action_button(
            maintenance_card,
            text="Track Request",
            command=lambda: self.track_maintenance_request(1),
        )

    def load_complaints_content(self, row):
        complaints_card = pe.function_card(row, "Complaints", side="left")

        pe.action_button(
            complaints_card,
            text="Register Complaint",
            command=lambda: self.register_complaint(1, "Noise complaint"),
        )


# ============================= ^ Homepage UI Content ^ =====================================

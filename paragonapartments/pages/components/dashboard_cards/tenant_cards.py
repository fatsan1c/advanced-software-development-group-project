"""Tenant-management dashboard card builders."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe


def load_front_desk_tenant_card(self, row):
    tenant_card = pe.FunctionCard(row, "Tenant Management", side="left")

    # Get available apartments for this location (vacant only)
    all_apartments = self.get_all_apartments(location="all")
    location_apartments_list = [
        apt for apt in all_apartments if apt["city"] == self.location and apt["occupied"] == 0
    ]

    # Format apartment options with more details
    apartment_options = [
        f"{apt['apartment_address']} - {apt['number_of_beds']} beds - £{apt['monthly_rent']}/month"
        for apt in location_apartments_list
    ]

    # Create tenant registration form with popup
    register_button, register_popup_func = pe.PopupCard(
        tenant_card,
        button_text="Register New Tenant",
        title="Tenant Registration",
        small=False,
        button_size="large",
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
            text_color=("#1a3c5c", "#4196E0"),
        )
        section_label.pack(fill="x", pady=(0, 15))

        # First Name
        fname_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        fname_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            fname_frame,
            text="First Name *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["First Name"] = ctk.CTkEntry(
            fname_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="Enter first name",
        )
        entries["First Name"].pack(fill="x")

        # Last Name
        lname_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        lname_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            lname_frame,
            text="Last Name *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Last Name"] = ctk.CTkEntry(
            lname_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="Enter last name",
        )
        entries["Last Name"].pack(fill="x")

        # Date of Birth
        dob_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        dob_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            dob_frame,
            text="Date of Birth *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Date of Birth"] = ctk.CTkEntry(
            dob_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="YYYY-MM-DD (e.g., 1990-01-15)",
        )
        entries["Date of Birth"].pack(fill="x")

        # NI Number
        ni_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        ni_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            ni_frame,
            text="National Insurance Number *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["NI Number"] = ctk.CTkEntry(
            ni_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="AB123456C",
        )
        entries["NI Number"].pack(fill="x")

        # === CONTACT INFORMATION SECTION ===
        section_label2 = ctk.CTkLabel(
            scrollable,
            text="━━━━━━━━━━━━ Contact Information ━━━━━━━━━━━━",
            font=("Arial", 14, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        )
        section_label2.pack(fill="x", pady=(15, 15))

        # Email
        email_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        email_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            email_frame,
            text="Email Address *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Email"] = ctk.CTkEntry(
            email_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="example@email.com",
        )
        entries["Email"].pack(fill="x")

        # Phone
        phone_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        phone_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            phone_frame,
            text="Phone Number *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Phone"] = ctk.CTkEntry(
            phone_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="07123456789",
        )
        entries["Phone"].pack(fill="x")

        # === TENANT DETAILS SECTION ===
        section_label3 = ctk.CTkLabel(
            scrollable,
            text="━━━━━━━━━━━━ Tenant Details ━━━━━━━━━━━━",
            font=("Arial", 14, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        )
        section_label3.pack(fill="x", pady=(15, 15))

        # Occupation
        occ_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        occ_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            occ_frame,
            text="Occupation",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Occupation"] = ctk.CTkEntry(
            occ_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="Job title (optional)",
        )
        entries["Occupation"].pack(fill="x")

        # Annual Salary
        salary_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        salary_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            salary_frame,
            text="Annual Salary (£)",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Annual Salary"] = ctk.CTkEntry(
            salary_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="e.g., 30000 (optional)",
        )
        entries["Annual Salary"].pack(fill="x")

        # Pets
        pets_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        pets_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            pets_frame,
            text="Pets *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Pets"] = ctk.CTkOptionMenu(
            pets_frame,
            values=["N", "Y"],
            height=40,
            font=("Arial", 14),
            fg_color=("#1a3c5c", "#4196E0"),
            button_color=("#0d2438", "#3380CC"),
            button_hover_color=("#0a1d2e", "#2570B8"),
        )
        entries["Pets"].set("N")
        entries["Pets"].pack(fill="x")

        # Right to Rent
        rtr_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        rtr_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            rtr_frame,
            text="Right to Rent *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Right to Rent"] = ctk.CTkOptionMenu(
            rtr_frame,
            values=["N", "Y"],
            height=40,
            font=("Arial", 14),
            fg_color=("#1a3c5c", "#4196E0"),
            button_color=("#0d2438", "#3380CC"),
            button_hover_color=("#0a1d2e", "#2570B8"),
        )
        entries["Right to Rent"].set("N")
        entries["Right to Rent"].pack(fill="x")

        # Credit Check
        cc_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        cc_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            cc_frame,
            text="Credit Check Status *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Credit Check"] = ctk.CTkOptionMenu(
            cc_frame,
            values=["Pending", "Approved", "Rejected"],
            height=40,
            font=("Arial", 14),
            fg_color=("#1a3c5c", "#4196E0"),
            button_color=("#0d2438", "#3380CC"),
            button_hover_color=("#0a1d2e", "#2570B8"),
        )
        entries["Credit Check"].set("Pending")
        entries["Credit Check"].pack(fill="x")

        # === PROPERTY & LEASE SECTION ===
        section_label4 = ctk.CTkLabel(
            scrollable,
            text="━━━━━━━━━━━━ Property & Lease Information ━━━━━━━━━━━━",
            font=("Arial", 14, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        )
        section_label4.pack(fill="x", pady=(15, 15))

        # City
        city_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        city_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            city_frame,
            text="Location *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["City"] = ctk.CTkOptionMenu(
            city_frame,
            values=[self.location],
            height=40,
            font=("Arial", 14),
            fg_color=("#1a3c5c", "#4196E0"),
            button_color=("#0d2438", "#3380CC"),
            button_hover_color=("#0a1d2e", "#2570B8"),
        )
        entries["City"].set(self.location)
        entries["City"].pack(fill="x")

        # Apartment
        apt_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        apt_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            apt_frame,
            text="Select Apartment *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        apt_options = apartment_options if apartment_options else ["No vacant apartments"]
        entries["Apartment"] = ctk.CTkOptionMenu(
            apt_frame,
            values=apt_options,
            height=40,
            font=("Arial", 14),
            fg_color=("#1a3c5c", "#4196E0"),
            button_color=("#0d2438", "#3380CC"),
            button_hover_color=("#0a1d2e", "#2570B8"),
        )
        entries["Apartment"].set(apt_options[0])
        entries["Apartment"].pack(fill="x")

        # Contract Start Date
        start_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        start_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            start_frame,
            text="Contract Start Date *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Contract Start Date"] = ctk.CTkEntry(
            start_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="YYYY-MM-DD (e.g., 2026-03-01)",
        )
        entries["Contract Start Date"].pack(fill="x")

        # Contract End Date
        end_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        end_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            end_frame,
            text="Contract End Date *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["Contract End Date"] = ctk.CTkEntry(
            end_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="YYYY-MM-DD (e.g., 2027-03-01)",
        )
        entries["Contract End Date"].pack(fill="x")

        # Status messages
        status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        status_frame.pack(fill="x", pady=(15, 0))

        error_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=("Arial", 13, "bold"),
            text_color=("#C41E3A", "#FF6B6B"),
        )
        success_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        )

        def handle_submit():
            error_label.pack_forget()
            success_label.pack_forget()

            # Validate required fields
            required_fields = [
                "First Name",
                "Last Name",
                "Date of Birth",
                "NI Number",
                "Email",
                "Phone",
                "Contract Start Date",
                "Contract End Date",
            ]
            for field in required_fields:
                value = entries[field].get().strip() if field in entries else ""
                if not value:
                    error_label.configure(text=f"❌ Error: {field} is required")
                    error_label.pack(pady=10)
                    return

            # Check if apartment is available
            if entries["Apartment"].get() == "No vacant apartments":
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
                        entry_widget.delete(0, "end")
                    elif isinstance(entry_widget, ctk.CTkOptionMenu) and field_name not in ["City"]:
                        if field_name in ["Pets", "Right to Rent"]:
                            entry_widget.set("N")
                        elif field_name == "Credit Check":
                            entry_widget.set("Pending")
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
            hover_color=("#0d2438", "#3380CC"),
        )
        submit_btn.pack(fill="x", pady=(20, 10))

    register_button.configure(command=setup_registration_popup)

    # Create tenant search popup
    search_button, search_popup_func = pe.PopupCard(
        tenant_card,
        button_text="Search Tenants",
        title="Tenant Information Lookup",
        small=False,
        button_size="large",
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
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 8))

        search_input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_input_frame.pack(fill="x")

        search_entry = ctk.CTkEntry(
            search_input_frame,
            placeholder_text="Enter search term...",
            height=45,
            font=("Arial", 14),
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
            hover_color=("#0d2438", "#3380CC"),
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
            hover_color=("#0a5d61", "#108B90"),
        )
        view_all_btn.pack(side="right")

        # Results area
        results_frame = ctk.CTkScrollableFrame(content, fg_color="transparent")
        results_frame.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        def display_tenant_results(results, search_term=""):
            """Helper function to display tenant results."""
            # Clear previous results
            for widget in results_frame.winfo_children():
                widget.destroy()

            if not results:
                no_results = ctk.CTkLabel(
                    results_frame,
                    text=f"❌ No tenants found{' matching ' + repr(search_term) if search_term else ''} in {self.location}",
                    font=("Arial", 14),
                    text_color=("#C41E3A", "#FF6B6B"),
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
                text_color=("#1a3c5c", "#4196E0"),
            )
            header.pack(pady=(0, 15))

            # Display each tenant in a card
            for tenant in results:
                tenant_card_frame = ctk.CTkFrame(
                    results_frame,
                    fg_color=("gray90", "gray17"),
                    corner_radius=10,
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
                    anchor="w",
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
                    anchor="w",
                ).pack(fill="x", pady=2)

                ctk.CTkLabel(
                    left_col,
                    text=f"📧 Email: {tenant.get('email', 'N/A')}",
                    font=("Arial", 12),
                    anchor="w",
                ).pack(fill="x", pady=2)

                ctk.CTkLabel(
                    left_col,
                    text=f"📱 Phone: {tenant.get('phone', 'N/A')}",
                    font=("Arial", 12),
                    anchor="w",
                ).pack(fill="x", pady=2)

                # Right column
                right_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                right_col.pack(side="right", fill="both", expand=True)

                ctk.CTkLabel(
                    right_col,
                    text=f"🎂 DOB: {tenant.get('date_of_birth', 'N/A')}",
                    font=("Arial", 12),
                    anchor="w",
                ).pack(fill="x", pady=2)

                ctk.CTkLabel(
                    right_col,
                    text=f"🆔 NI: {tenant.get('NI_number', 'N/A')}",
                    font=("Arial", 12),
                    anchor="w",
                ).pack(fill="x", pady=2)

                ctk.CTkLabel(
                    right_col,
                    text=f"💼 Occupation: {tenant.get('occupation', 'N/A') or 'N/A'}",
                    font=("Arial", 12),
                    anchor="w",
                ).pack(fill="x", pady=2)

                # View full details button
                tenant_id = tenant.get("tenant_ID")

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
                            hover_color=("gray65", "gray25"),
                        )
                        back_btn.pack(fill="x", pady=(0, 15))

                        # Full details card
                        details_card = ctk.CTkFrame(
                            results_frame,
                            fg_color=("gray90", "gray17"),
                            corner_radius=10,
                        )
                        details_card.pack(fill="both", expand=True)

                        info_label = ctk.CTkLabel(
                            details_card,
                            text=info_text,
                            font=("Arial", 13),
                            justify="left",
                            anchor="nw",
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
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(pady=(0, 20))

                        # Personal Information
                        section_label = ctk.CTkLabel(
                            scrollable_edit,
                            text="━━━━━━━━━━━━ Personal Information ━━━━━━━━━━━━",
                            font=("Arial", 14, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        )
                        section_label.pack(fill="x", pady=(0, 15))

                        # First Name
                        fname_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        fname_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            fname_frame,
                            text="First Name *",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["First Name"] = ctk.CTkEntry(fname_frame, height=40, font=("Arial", 14))
                        entries["First Name"].insert(0, tenant_data.get("first_name", ""))
                        entries["First Name"].pack(fill="x")

                        # Last Name
                        lname_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        lname_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            lname_frame,
                            text="Last Name *",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["Last Name"] = ctk.CTkEntry(lname_frame, height=40, font=("Arial", 14))
                        entries["Last Name"].insert(0, tenant_data.get("last_name", ""))
                        entries["Last Name"].pack(fill="x")

                        # Date of Birth
                        dob_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        dob_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            dob_frame,
                            text="Date of Birth *",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["Date of Birth"] = ctk.CTkEntry(dob_frame, height=40, font=("Arial", 14))
                        entries["Date of Birth"].insert(0, tenant_data.get("date_of_birth", ""))
                        entries["Date of Birth"].pack(fill="x")

                        # NI Number
                        ni_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        ni_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            ni_frame,
                            text="National Insurance Number *",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["NI Number"] = ctk.CTkEntry(ni_frame, height=40, font=("Arial", 14))
                        entries["NI Number"].insert(0, tenant_data.get("NI_number", ""))
                        entries["NI Number"].pack(fill="x")

                        # Contact Information
                        section_label2 = ctk.CTkLabel(
                            scrollable_edit,
                            text="━━━━━━━━━━━━ Contact Information ━━━━━━━━━━━━",
                            font=("Arial", 14, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        )
                        section_label2.pack(fill="x", pady=(15, 15))

                        # Email
                        email_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        email_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            email_frame,
                            text="Email Address *",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["Email"] = ctk.CTkEntry(email_frame, height=40, font=("Arial", 14))
                        entries["Email"].insert(0, tenant_data.get("email", ""))
                        entries["Email"].pack(fill="x")

                        # Phone
                        phone_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        phone_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            phone_frame,
                            text="Phone Number *",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["Phone"] = ctk.CTkEntry(phone_frame, height=40, font=("Arial", 14))
                        entries["Phone"].insert(0, tenant_data.get("phone", ""))
                        entries["Phone"].pack(fill="x")

                        # Tenant Details
                        section_label3 = ctk.CTkLabel(
                            scrollable_edit,
                            text="━━━━━━━━━━━━ Tenant Details ━━━━━━━━━━━━",
                            font=("Arial", 14, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        )
                        section_label3.pack(fill="x", pady=(15, 15))

                        # Occupation
                        occ_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        occ_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            occ_frame,
                            text="Occupation",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["Occupation"] = ctk.CTkEntry(occ_frame, height=40, font=("Arial", 14))
                        entries["Occupation"].insert(0, tenant_data.get("occupation", "") or "")
                        entries["Occupation"].pack(fill="x")

                        # Annual Salary
                        salary_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        salary_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            salary_frame,
                            text="Annual Salary (£)",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["Annual Salary"] = ctk.CTkEntry(salary_frame, height=40, font=("Arial", 14))
                        salary_val = str(tenant_data.get("annual_salary", "")) if tenant_data.get("annual_salary") else ""
                        entries["Annual Salary"].insert(0, salary_val)
                        entries["Annual Salary"].pack(fill="x")

                        # Pets
                        pets_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        pets_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            pets_frame,
                            text="Pets *",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["Pets"] = ctk.CTkOptionMenu(
                            pets_frame,
                            values=["N", "Y"],
                            height=40,
                            font=("Arial", 14),
                            fg_color=("#1a3c5c", "#4196E0"),
                        )
                        entries["Pets"].set(tenant_data.get("pets", "N"))
                        entries["Pets"].pack(fill="x")

                        # Right to Rent
                        rtr_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        rtr_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            rtr_frame,
                            text="Right to Rent *",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["Right to Rent"] = ctk.CTkOptionMenu(
                            rtr_frame,
                            values=["N", "Y"],
                            height=40,
                            font=("Arial", 14),
                            fg_color=("#1a3c5c", "#4196E0"),
                        )
                        entries["Right to Rent"].set(tenant_data.get("right_to_rent", "N"))
                        entries["Right to Rent"].pack(fill="x")

                        # Credit Check
                        cc_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        cc_frame.pack(fill="x", pady=(0, 12))
                        ctk.CTkLabel(
                            cc_frame,
                            text="Credit Check Status *",
                            font=("Arial", 13, "bold"),
                            text_color=("#1a3c5c", "#4196E0"),
                        ).pack(anchor="w", pady=(0, 5))
                        entries["Credit Check"] = ctk.CTkOptionMenu(
                            cc_frame,
                            values=["Pending", "Approved", "Rejected"],
                            height=40,
                            font=("Arial", 14),
                            fg_color=("#1a3c5c", "#4196E0"),
                        )
                        entries["Credit Check"].set(tenant_data.get("credit_check", "Pending"))
                        entries["Credit Check"].pack(fill="x")

                        # Status messages
                        status_frame = ctk.CTkFrame(scrollable_edit, fg_color="transparent")
                        status_frame.pack(fill="x", pady=(15, 0))

                        error_label = ctk.CTkLabel(
                            status_frame,
                            text="",
                            font=("Arial", 13, "bold"),
                            text_color=("#C41E3A", "#FF6B6B"),
                        )
                        success_label = ctk.CTkLabel(
                            status_frame,
                            text="",
                            font=("Arial", 13, "bold"),
                            text_color=("#2D862D", "#4CAF50"),
                        )

                        def handle_update():
                            error_label.pack_forget()
                            success_label.pack_forget()

                            # Validate required fields
                            required_fields = [
                                "First Name",
                                "Last Name",
                                "Date of Birth",
                                "NI Number",
                                "Email",
                                "Phone",
                            ]
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
                            hover_color=("#0d2438", "#3380CC"),
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
                            hover_color=("gray60", "gray25"),
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
                    hover_color=("#0d2438", "#3380CC"),
                )
                view_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

                edit_btn = ctk.CTkButton(
                    buttons_frame,
                    text="✏️ Edit Tenant",
                    command=create_edit_tenant(tenant_id, tenant),
                    height=38,
                    font=("Arial", 13, "bold"),
                    fg_color=("#0d7377", "#14A9AF"),
                    hover_color=("#0a5d61", "#108B90"),
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
                    text_color=("#FFA500", "#FF8C00"),
                )
                error_msg.pack(pady=20)
                return

            # Search by ID if numeric
            if search_term.isdigit():
                result = self.get_tenant_by_id(int(search_term))
                results = [result] if result else []
            else:
                # Search by name, email, etc.
                results = self.search_tenants(search_term)

            display_tenant_results(results, search_term)

        def view_all_tenants():
            """View all tenants in this location."""
            search_entry.delete(0, "end")
            results = self.get_all_tenants()
            display_tenant_results(results, "")

        # Bind Enter key to search
        search_entry.bind("<Return>", lambda _e: perform_search())

        # Show initial message
        initial_msg = ctk.CTkLabel(
            results_frame,
            text="👆 Enter a search term above to find tenants",
            font=("Arial", 14),
            text_color=("gray50", "gray60"),
        )
        initial_msg.pack(pady=40)

    search_button.configure(command=setup_search_popup)

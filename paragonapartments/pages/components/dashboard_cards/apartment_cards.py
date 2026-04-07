"""Apartment-related dashboard card builders."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe


def _apartment_status(apartment) -> str:
    status = apartment.get("status")
    if status in {"Vacant", "Occupied"}:
        return status

    occupied = apartment.get("occupied", 0)
    try:
        return "Occupied" if int(occupied) == 1 else "Vacant"
    except (TypeError, ValueError):
        return "Unknown"


def load_admin_apartment_card(self, row):
    apartment_card = pe.FunctionCard(row, f"Manage Apartments - {self.location}", side="top", pady=6, padx=8)

    fields = [
        {"name": "Apartment Address", "type": "text", "required": True, "placeholder": "Apartment 123"},
        {"name": "Number of Beds", "type": "text", "subtype": "number", "required": True, "placeholder": "0"},
        {
            "name": "Monthly Rent",
            "type": "text",
            "subtype": "currency",
            "required": True,
            "placeholder": "£0.00",
        },
        {"name": "Status", "type": "dropdown", "options": ["Vacant", "Occupied"], "required": True},
    ]

    pe.Form(
        apartment_card,
        fields,
        name="Add Apartment",
        submit_text="Add Apartment",
        on_submit=self.add_apartment,
        field_per_row=4,
    )

    button, open_popup_func = pe.PopupCard(
        apartment_card,
        button_text="Edit Apartments",
        title=f"Edit Apartments - {self.location}",
        small=False,
        button_size="full",
    )
    pe.style_secondary_button(button)

    def setup_popup():
        content = open_popup_func()

        columns = [
            {"name": "ID", "key": "apartment_ID", "width": 80, "editable": False},
            {"name": "Address", "key": "apartment_address", "width": 200},
            {"name": "Beds", "key": "number_of_beds", "format": "number", "width": 80},
            {"name": "Monthly Rent", "key": "monthly_rent", "format": "currency", "width": 120},
            {"name": "Status", "key": "occupied", "width": 100, "format": "boolean", "options": ["Occupied", "Vacant"]},
            {"name": "Location", "key": "city", "width": 150, "editable": False},
        ]

        def get_data():
            try:
                return self.get_all_apartments(location=self.location)
            except Exception as e:
                print(f"Error loading apartments: {e}")
                return []

        pe.EditableTablePopup(
            content,
            columns,
            get_data_func=get_data,
            on_delete_func=self.delete_apartment,
            on_update_func=self.edit_apartment,
        )

    button.configure(command=setup_popup)


def load_front_desk_apartment_search_card(self, row):
    apartment_card = pe.FunctionCard(row, "Apartment Search", side="left")

    search_apt_button, search_apt_popup_func = pe.PopupCard(
        apartment_card,
        button_text="Search Apartments",
        title="Find Available Apartments",
        small=False,
        button_size="large",
    )

    def setup_apartment_search_popup():
        content = search_apt_popup_func()

        filter_frame = ctk.CTkFrame(content, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(
            filter_frame,
            text="🔍 Search Filters",
            font=("Arial", 16, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 15))

        filters = {}

        loc_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        loc_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(loc_frame, text="📍 Location", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
        filters["location"] = ctk.CTkOptionMenu(
            loc_frame,
            values=["All", self.location],
            height=40,
            font=("Arial", 14),
            fg_color=("#1a3c5c", "#4196E0"),
        )
        filters["location"].set(self.location)
        filters["location"].pack(fill="x")

        beds_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        beds_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(beds_frame, text="🛏️ Number of Bedrooms", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
        filters["beds"] = ctk.CTkOptionMenu(
            beds_frame,
            values=["Any", "1", "2", "3", "4", "5+"],
            height=40,
            font=("Arial", 14),
            fg_color=("#1a3c5c", "#4196E0"),
        )
        filters["beds"].set("Any")
        filters["beds"].pack(fill="x")

        status_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(status_frame, text="✅ Availability", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
        filters["status"] = ctk.CTkOptionMenu(
            status_frame,
            values=["All", "Vacant", "Occupied"],
            height=40,
            font=("Arial", 14),
            fg_color=("#1a3c5c", "#4196E0"),
        )
        filters["status"].set("All")
        filters["status"].pack(fill="x")

        price_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        price_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(price_frame, text="💰 Max Monthly Rent (£)", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
        filters["max_rent"] = ctk.CTkEntry(
            price_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="Leave blank for no limit",
        )
        filters["max_rent"].pack(fill="x")

        search_btn = ctk.CTkButton(
            filter_frame,
            text="🔎 Search Apartments",
            command=lambda: perform_apartment_search(),
            height=50,
            font=("Arial", 16, "bold"),
            fg_color=("#1a3c5c", "#4196E0"),
            hover_color=("#0d2438", "#3380CC"),
        )
        search_btn.pack(fill="x", pady=(10, 0))

        results_frame = ctk.CTkScrollableFrame(content, fg_color="transparent")
        results_frame.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        def display_apartment_results(apartments):
            for widget in results_frame.winfo_children():
                widget.destroy()

            if not apartments:
                no_results = ctk.CTkLabel(
                    results_frame,
                    text="❌ No apartments found matching your criteria",
                    font=("Arial", 14),
                    text_color=("#C41E3A", "#FF6B6B"),
                )
                no_results.pack(pady=20)
                return

            header_text = f"✓ Found {len(apartments)} apartment{'s' if len(apartments) > 1 else ''}"
            header = ctk.CTkLabel(
                results_frame,
                text=header_text,
                font=("Arial", 15, "bold"),
                text_color=("#1a3c5c", "#4196E0"),
            )
            header.pack(pady=(0, 15))

            for apt in apartments:
                apt_card_frame = ctk.CTkFrame(
                    results_frame,
                    fg_color=("gray90", "gray17"),
                    corner_radius=10,
                )
                apt_card_frame.pack(fill="x", pady=(0, 12))

                content_frame = ctk.CTkFrame(apt_card_frame, fg_color="transparent")
                content_frame.pack(fill="both", expand=True, padx=20, pady=15)

                header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                header_frame.pack(fill="x", pady=(0, 10))

                address_label = ctk.CTkLabel(
                    header_frame,
                    text=f"🏠 {apt.get('apartment_address', 'N/A')}",
                    font=("Arial", 16, "bold"),
                    text_color=("#1a3c5c", "#4196E0"),
                    anchor="w",
                )
                address_label.pack(side="left", fill="x", expand=True)

                status = _apartment_status(apt)
                if status == "Vacant":
                    status_color = ("#2D862D", "#4CAF50")
                    status_text = "✅ VACANT"
                elif status == "Occupied":
                    status_color = ("#C41E3A", "#FF6B6B")
                    status_text = "🔴 OCCUPIED"
                else:
                    status_color = ("#5F6368", "#80868B")
                    status_text = "❔ UNKNOWN"

                status_badge = ctk.CTkLabel(
                    header_frame,
                    text=status_text,
                    font=("Arial", 11, "bold"),
                    text_color="white",
                    fg_color=status_color,
                    corner_radius=5,
                )
                status_badge.pack(side="right", ipadx=10, ipady=5)

                details_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                details_frame.pack(fill="x", pady=(0, 10))

                left_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                left_col.pack(side="left", fill="both", expand=True)

                ctk.CTkLabel(
                    left_col,
                    text=f"🆔 Apartment ID: {apt.get('apartment_ID', 'N/A')}",
                    font=("Arial", 12),
                    anchor="w",
                ).pack(fill="x", pady=2)

                ctk.CTkLabel(
                    left_col,
                    text=f"🛏️ Bedrooms: {apt.get('number_of_beds', 'N/A')}",
                    font=("Arial", 12),
                    anchor="w",
                ).pack(fill="x", pady=2)

                right_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                right_col.pack(side="right", fill="both", expand=True)

                ctk.CTkLabel(
                    right_col,
                    text=f"📍 Location: {apt.get('city', 'N/A')}",
                    font=("Arial", 12),
                    anchor="w",
                ).pack(fill="x", pady=2)

                ctk.CTkLabel(
                    right_col,
                    text=f"💰 Monthly Rent: £{apt.get('monthly_rent', 'N/A')}",
                    font=("Arial", 12),
                    anchor="w",
                ).pack(fill="x", pady=2)

        def perform_apartment_search():
            all_apartments = self.get_all_apartments(location="all")
            filtered = all_apartments

            location_filter = filters["location"].get()
            if location_filter != "All":
                filtered = [a for a in filtered if a["city"] == location_filter]

            beds_filter = filters["beds"].get()
            if beds_filter != "Any":
                if beds_filter == "5+":
                    filtered = [a for a in filtered if a["number_of_beds"] >= 5]
                else:
                    filtered = [a for a in filtered if a["number_of_beds"] == int(beds_filter)]

            status_filter = filters["status"].get()
            if status_filter != "All":
                filtered = [a for a in filtered if _apartment_status(a) == status_filter]

            max_rent = filters["max_rent"].get().strip()
            if max_rent and max_rent.isdigit():
                filtered = [a for a in filtered if a["monthly_rent"] <= int(max_rent)]

            display_apartment_results(filtered)

        initial_msg = ctk.CTkLabel(
            results_frame,
            text="👆 Set your filters and click Search to find apartments",
            font=("Arial", 14),
            text_color=("gray50", "gray60"),
        )
        initial_msg.pack(pady=40)

    search_apt_button.configure(command=setup_apartment_search_popup)

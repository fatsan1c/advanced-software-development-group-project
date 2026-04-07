"""Business management dashboard card builders."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe


def load_manager_business_expansion_card(self, row):
    expand_card = pe.FunctionCard(row, "Expand Business", side="top", pady=6, padx=8)

    main_row = ctk.CTkFrame(expand_card, fg_color="transparent")
    main_row.pack(fill="both", expand=True)

    left_col = ctk.CTkFrame(main_row, fg_color="transparent")
    left_col.pack(side="left", fill="both", expand=True, padx=(0, 12))

    right_col = ctk.CTkFrame(main_row, fg_color="transparent")
    right_col.pack(side="left", fill="both", expand=True, padx=(12, 0))

    location_fields = [
        {"name": "City", "type": "text", "required": True, "placeholder": "New city name"},
        {"name": "Address", "type": "text", "required": True, "placeholder": "Full address"},
    ]
    pe.Form(
        left_col,
        location_fields,
        name="Add Location",
        submit_text="Add Location",
        on_submit=self.expand_business,
    )

    loc_btn, open_loc_popup = pe.PopupCard(
        left_col,
        button_text="Edit Locations",
        title="Edit Locations",
        small=False,
        button_size="full",
    )
    pe.style_secondary_button(loc_btn)

    def setup_loc_popup():
        content = open_loc_popup()

        columns = [
            {"name": "ID", "key": "location_ID", "width": 80, "editable": False},
            {"name": "City", "key": "city", "width": 200},
            {"name": "Address", "key": "address", "width": 200},
        ]

        def get_data():
            try:
                return self.get_all_locations()
            except Exception as e:
                print(f"Error loading locations: {e}")
                return []

        pe.EditableTablePopup(
            content,
            columns,
            get_data_func=get_data,
            on_delete_func=self.delete_location,
            on_update_func=self.edit_location,
        )

    loc_btn.configure(command=setup_loc_popup)

    try:
        location_options = self.get_all_cities()
    except Exception as e:
        print(f"Error loading locations: {e}")
        location_options = []

    apartment_fields = [
        {"name": "Location", "type": "dropdown", "options": location_options, "required": True},
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
        right_col,
        apartment_fields,
        name="Add Apartment",
        submit_text="Add Apartment",
        on_submit=self.add_apartment,
        field_per_row=2,
    )

    apt_btn, open_apt_popup = pe.PopupCard(
        right_col,
        button_text="Edit Apartments",
        title="Edit Apartments",
        small=False,
        button_size="full",
    )
    pe.style_secondary_button(apt_btn)

    def setup_apt_popup():
        content = open_apt_popup()

        columns = [
            {"name": "ID", "key": "apartment_ID", "width": 80, "editable": False},
            {"name": "Location", "key": "city", "width": 150, "format": "dropdown", "options": location_options},
            {"name": "Address", "key": "apartment_address", "width": 150},
            {"name": "Beds", "key": "number_of_beds", "width": 80, "format": "number"},
            {"name": "Monthly Rent", "key": "monthly_rent", "width": 120, "format": "currency"},
            {
                "name": "Status",
                "key": "occupied",
                "width": 100,
                "format": "boolean",
                "options": ["Occupied", "Vacant"],
            },
        ]

        def get_data(location):
            try:
                return self.get_all_apartments(location)
            except Exception as e:
                print(f"Error loading apartments: {e}")
                return []

        pe.EditableTablePopup(
            content,
            columns,
            get_data_func=get_data,
            on_delete_func=self.delete_apartment,
            on_update_func=self.edit_apartment,
            include_location_filter=True,
            location_mapper=pe.normalize_location_value,
        )

    apt_btn.configure(command=setup_apt_popup)

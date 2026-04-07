"""Account-management dashboard card builders."""

from __future__ import annotations

import pages.components.page_elements as pe


def load_admin_account_card(self, row):
    """Render administrator account card."""
    accounts_card = pe.FunctionCard(row, f"Manage Accounts - {self.location}", side="left", pady=6, padx=8)

    fields = [
        {"name": "Username", "type": "text", "required": True, "placeholder": "Unique username"},
        {"name": "Role", "type": "dropdown", "options": ["Admin", "Frontdesk", "Maintenance"], "required": True},
        {"name": "Password", "type": "text", "required": True, "placeholder": "Secure password"},
    ]

    pe.Form(
        accounts_card,
        fields,
        name="Create Account",
        submit_text="Create Account",
        on_submit=self.create_account,
    )

    button, open_popup_func = pe.PopupCard(
        accounts_card,
        button_text="Edit Accounts",
        title=f"Edit Accounts - {self.location}",
        small=False,
        button_size="full",
    )
    pe.style_secondary_button(button)

    def setup_popup():
        content = open_popup_func()

        columns = [
            {"name": "ID", "key": "user_ID", "width": 80, "editable": False},
            {"name": "Username", "key": "username", "width": 200},
            {"name": "Location", "key": "city", "width": 200, "editable": False},
            {
                "name": "Role",
                "key": "role",
                "width": 150,
                "format": "dropdown",
                "options": ["Admin", "Frontdesk", "Maintenance"],
            },
        ]

        def get_data():
            try:
                return self.get_all_users(self.location)
            except Exception as e:
                print(f"Error loading users: {e}")
                return []

        pe.EditableTablePopup(
            content,
            columns,
            get_data_func=get_data,
            on_delete_func=self.delete_account,
            on_update_func=self.edit_account,
        )

    button.configure(command=setup_popup)


def load_manager_account_card(self, row):
    """Render manager account card."""
    accounts_card = pe.FunctionCard(row, "Manage Accounts", side="left", pady=6, padx=8)

    try:
        location_options = ["None"] + self.get_all_cities()
    except Exception as e:
        print(f"Error loading locations: {e}")
        location_options = ["None"]

    fields = [
        {"name": "Username", "type": "text", "required": True, "placeholder": "Unique username"},
        {
            "name": "Role",
            "type": "dropdown",
            "options": ["Admin", "Manager", "Finance Manager", "Frontdesk", "Maintenance"],
            "required": True,
        },
        {"name": "Password", "type": "text", "required": True, "placeholder": "Secure password"},
        {"name": "Location", "type": "dropdown", "options": location_options, "required": False},
    ]

    pe.Form(
        accounts_card,
        fields,
        name="Create Account",
        submit_text="Create Account",
        on_submit=self.create_account,
    )

    button, open_popup_func = pe.PopupCard(
        accounts_card,
        button_text="Edit Accounts",
        title="Edit Accounts",
        small=False,
        button_size="full",
    )
    pe.style_secondary_button(button)

    def setup_popup():
        content = open_popup_func()

        columns = [
            {"name": "ID", "key": "user_ID", "width": 80, "editable": False},
            {"name": "Username", "key": "username", "width": 200},
            {
                "name": "Location",
                "key": "city",
                "width": 200,
                "format": "dropdown",
                "options": ["None"] + self.get_all_cities(),
            },
            {
                "name": "Role",
                "key": "role",
                "width": 150,
                "format": "dropdown",
                "options": ["Admin", "Manager", "Finance Manager", "Frontdesk", "Maintenance"],
            },
        ]

        def get_data():
            try:
                return self.get_all_users()
            except Exception as e:
                print(f"Error loading users: {e}")
                return []

        pe.EditableTablePopup(
            content,
            columns,
            get_data_func=get_data,
            on_delete_func=self.delete_account,
            on_update_func=self.edit_account,
        )

    button.configure(command=setup_popup)

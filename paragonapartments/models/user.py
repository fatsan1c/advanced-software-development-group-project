"""Contributors: Aaron Antal-Bento (23013693)"""

import customtkinter as ctk
import pages.components.page_elements as pe
from models.role_types import RoleType, parse_role, role_label
from pages.components.config.theme import THEME
from services.account_service import AccountService


def _build_user_factory_registry():
    """Build role-to-class factory registry lazily to avoid import cycles."""
    from models.user_roles.administrator import Administrator
    from models.user_roles.manager import Manager
    from models.user_roles.finance_manager import FinanceManager
    from models.user_roles.front_desk_staff import FrontDeskStaff
    from models.user_roles.maintenance_staff import MaintenanceStaff

    return {
        RoleType.ADMINISTRATOR: Administrator,
        RoleType.MANAGER: Manager,
        RoleType.FINANCE_MANAGER: FinanceManager,
        RoleType.FRONT_DESK_STAFF: FrontDeskStaff,
        RoleType.MAINTENANCE_STAFF: MaintenanceStaff,
    }


def create_user(username: str, user_type: str, location: str = ""):
    """Factory function to create the appropriate user class based on user type."""
    role_type = parse_role(user_type)
    user_factory = _build_user_factory_registry().get(role_type)
    if user_factory is not None:
        return user_factory(username, location)

    return User(username, role_label(user_type), location)


class User:
    """Base user class for all user types in the system."""
    
    def __init__(self, username: str, role: str | RoleType, location: str = ""):
        self.username = username
        self.role = role_label(role)
        self.role_type = parse_role(role)
        self.location = location
    
    def view_profile(self):
        """Return a string representation of the user profile."""
        return f"User(username='{self.username}', role='{self.role}', location='{self.location}')"
    
    def logout(self, home_page):
        """Log the user out of the system."""
        print(f"{self.username} has logged out.")
        home_page.close_page()

    def change_password(self, values):
        """Change the user's password."""
        old_password = values.get('Current Password', '')
        new_password = values.get('New Password', '')

        try:
            success = AccountService.change_password(self.username, old_password, new_password)

            if success:
                return True
            else:
                return "Failed to change password. Please check your old password."
        except Exception as e:
            return f"Failed to change password: {str(e)}"

    def load_homepage_content(self, home_page):
        """Initialize and display home page content."""
        # Centered content wrapper
        top_content = pe.ContentContainer(parent=home_page, anchor="nw", fill="x", marginy=(10, 0))

        # Display role and "Dashboard" in the center
        ctk.CTkLabel(
            top_content, 
            text=self.role + " Dashboard" + (f" - {self.location}" if self.location else ""),
            font=("Arial", 24)
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Change password popup trigger in the top right corner, next to logout
        _, open_popup = pe.PopupCard(home_page, title="Change Password", small=True, generate_button=False)

        def setup_popup():
            content = open_popup()

            # Define the fields for changing password
            fields = [
                {'name': 'Current Password', 'type': 'text', 'subtype': 'password', 'required': True, 'placeholder': '• • • • • • • •'},
                {'name': 'New Password', 'type': 'text', 'subtype': 'password', 'required': True, 'placeholder': '• • • • • • • •'},
            ]
            pe.Form(content, fields, name="Change Password", submit_text="Change Password", on_submit=self.change_password)

        # Top-right account actions
        actions = ctk.CTkFrame(top_content, fg_color="transparent")
        actions.pack(side="right", padx=10)

        ctk.CTkButton(
            actions,
            text="Logout",
            width=96,
            height=36,
            font=("Arial", 14, "bold"),
            command=lambda: self.logout(home_page),
            fg_color=(THEME.colors.primary_blue, THEME.colors.primary_blue),
            hover_color=(THEME.colors.primary_blue_hover, THEME.colors.primary_blue_hover),
        ).pack(anchor="e")

        ctk.CTkButton(
            home_page,
            text="Change Password",
            bg_color="transparent",
            fg_color="transparent",
            hover_color=("gray90", "gray20"),
            text_color=("black", "white"),
            height=12,
            width=10,
            command=setup_popup,
            font=("Arial", 10),
        ).pack(anchor="ne", padx=15, pady=0)

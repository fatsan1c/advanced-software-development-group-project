import customtkinter as ctk
import pages.components.page_elements as pe
import database_operations.repos.user_repository as user_repo


def create_user(username: str, user_type: str, location: str = ""):
    """Factory function to create the appropriate user class based on user type"""
    from models.user_roles.administrator import Administrator
    from models.user_roles.manager import Manager
    from models.user_roles.finance_manager import FinanceManager
    from models.user_roles.front_desk_staff import FrontDeskStaff
    from models.user_roles.maintenance_staff import MaintenanceStaff
    
    # Normalize user type for comparison
    user_type_lower = user_type.lower().replace(" ", "")
    
    # Check user type and return the corresponding user class instance
    if user_type_lower == "administrator" or user_type_lower == "admin":
        return Administrator(username, location)
    elif user_type_lower == "manager":
        return Manager(username, location)
    elif user_type_lower == "financemanager" or user_type_lower == "finance":
        return FinanceManager(username, location)
    elif user_type_lower == "frontdeskstaff" or user_type_lower == "frontdesk":
        return FrontDeskStaff(username, location)
    elif user_type_lower == "maintenancestaff" or user_type_lower == "maintenance":
        return MaintenanceStaff(username, location)
    else:
        return User(username, user_type, location)


class User:
    """Base user class for all user types in the system."""
    
    def __init__(self, username: str, role: str, location: str = ""):
        self.username = username
        self.role = role
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
        old_password = values.get('Old Password', '')
        new_password = values.get('New Password', '')

        try:
            # Request password change from the user repository
            success = user_repo.change_password(self.username, old_password, new_password)

            if success:
                return True
            else:
                return "Failed to change password. Please check your old password."
        except Exception as e:
            return f"Failed to change password: {str(e)}"

    def load_homepage_content(self, home_page):
        """Initialize and display home page content."""
        # Centered content wrapper
        top_content = pe.content_container(parent=home_page, anchor="nw", fill="x", marginy=(10, 0))

        # Display username and location in the top left corner
        ctk.CTkLabel(
            top_content, 
            text=self.username + (f" - {self.location}" if self.location else ""), 
            font=("Arial", 24)
        ).pack(side="left", padx=15)

        # Display role and "Dashboard" in the center
        ctk.CTkLabel(
            top_content, 
            text=self.role + " Dashboard",
            font=("Arial", 24)
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Logout button in the top right corner
        ctk.CTkButton(
            top_content, 
            text="Logout",
            width=80,
            height=40,
            font=("Arial", 17),
            command=lambda: self.logout(home_page)
        ).pack(side="right", padx=10)

        # Change password popup trigger in the top right corner, next to logout
        _, open_popup = pe.popup_card(home_page, title="Change Password", small=True, generate_button=False)

        def setup_popup():
            content = open_popup()

            # Define the fields for changing password
            fields = [
                {'name': 'Old Password', 'type': 'text', 'subtype': 'password', 'required': True},
                {'name': 'New Password', 'type': 'text', 'subtype': 'password', 'required': True},
            ]
            pe.form_element(content, fields, name="Change Password", submit_text="Change Password", on_submit=self.change_password, small=True)

        # Change password button
        ctk.CTkButton(
            home_page, 
            text="Change password",
            bg_color="transparent",
            fg_color="transparent",
            hover_color=("gray90", "gray20"),
            text_color=("black", "white"),
            height=12,
            width=10,
            command=setup_popup,
            font=("Arial", 10),
        ).pack(anchor="ne", padx=15, pady=0)

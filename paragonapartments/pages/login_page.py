import customtkinter as ctk
from database_operations.repos.user_repository import authenticate_user
import pages.components.page_elements as pe

class LoginPage(ctk.CTkToplevel):
    """Login page window for user authentication."""
    
    def __init__(self, controller, on_login_success=None):
        super().__init__()
        self.controller = controller
        self.on_login_success = on_login_success
        
        self.title("Paragon Apartment Login")
        width = 320
        height = 360
        geometry = controller.calculate_centered_geometry(width, height)
        self.geometry(geometry)
        
        # Container to hold all frames
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.loginpage_content(container)

    def loginpage_content(self, container):
        # Create inner frame for centered content
        inner_frame = pe.content_container(parent=container)
        inner_frame.place(relx=0.5, rely=0.57, anchor="center")
        
        ctk.CTkLabel(container, text="Paragon Apartments", font=("Arial", 24)).pack(pady=30)
        ctk.CTkLabel(inner_frame, text="Login", font=("Arial", 18)).pack(pady=(8, 2))

        pe.content_separator(inner_frame, pady=(5, 40))
        
        self.username_entry = ctk.CTkEntry(inner_frame, placeholder_text="Username", font=("Arial", 14))
        self.username_entry.pack(pady=6)
        self.password_entry = ctk.CTkEntry(inner_frame, placeholder_text="Password", show="*", font=("Arial", 14))
        self.password_entry.pack(pady=6)
        ctk.CTkButton(inner_frame, text="Login",
             command=lambda: self.authenticate(inner_frame, username=self.username_entry.get(), 
                                               password=self.password_entry.get())).pack(pady=(20, 40), padx=40)
    
    def authenticate(self, container, username: str, password: str) -> bool:
        """Authenticate user credentials."""
        # Authenticate against database
        user = authenticate_user(username, password)
        
        if user:
            print(f"Login successful: {user['username']} ({user['role']}), {user['city']}")
            self.complete_login(user['role'], user['city'])
            return True
        else:
            # Show error message
            if not hasattr(self, 'error_label'):
                self.error_label = ctk.CTkLabel(
                    container, 
                    text="Invalid credentials, please try again.", 
                    text_color="red"
                )
            self.error_label.pack()
            print("Login failed: Invalid username or password")
            return False

    def complete_login(self, user_type: str, location: str=None):
        """Complete login process and notify controller."""
        username = self.username_entry.get()
        
        # Call the success callback if provided
        if self.on_login_success:
            self.on_login_success(username, user_type, location)
        
        # Close the login window
        self.destroy()
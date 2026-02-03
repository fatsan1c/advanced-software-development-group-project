import customtkinter as ctk
from pages.home_page import HomePage
from pages.login_page import LoginPage
from models.user import create_user
from pathlib import Path


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Paragon Apartment Management Portal")
        width = 1000
        height = 650
        self.geometry(self.calculate_centered_geometry(width, height))

        # Resolve logos path relative to this file
        logos_dir = Path(__file__).parent / "icons/paragon_logos"
        self.dark_logo_path = str(logos_dir / "paragon_logo.ico")
        self.light_logo_path = str(logos_dir / "paragon_logo_light.ico")
        self.current_icon = self.light_logo_path

        # Set application icon using ICO file
        self.change_icon(mode="dark")
        
        # Container to hold all frames
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Store current user and page
        self.current_user = None
        
        # Show login page
        self.show_login()

        if self.current_user is not None:
            self.mainloop()

    def show_login(self):
        """Display the login page as a modal dialog."""
        login_page = self.open_page("LoginPage", controller=self, on_login_success=self.handle_login_success)
        self.wait_window(login_page)        
    
    def handle_login_success(self, username: str, user_type: str, location: str=None):
        """Handle successful login by creating user and showing home page.
        
        Args:
            username: The logged-in username
            password: The user's password
            user_type: The type/role of the user
        """
        # Create user object
        self.current_user = create_user(username, user_type, location)
        
        # Show home page
        self.open_page("HomePage", parent=self.container, controller=self, user=self.current_user)

    def open_page(self, page_name, **kwargs):
        if page_name == "HomePage":
            home_page = HomePage(kwargs.get("parent"), kwargs.get("controller"), kwargs.get("user"))
            home_page.grid(row=0, column=0, sticky="nsew")
            home_page.tkraise()
            return home_page
        elif page_name == "LoginPage":
            login_page = LoginPage(kwargs.get("controller"), on_login_success=kwargs.get("on_login_success"))
            return login_page
    
    def handle_logout(self):
        """Handle logout by clearing session and returning to login page."""
        # Clear current user reference
        self.current_user = None
        self.withdraw()
        
        # Show login page again
        self.show_login()
        
        if self.current_user is not None:
            self.deiconify()
        else:
            self.destroy()
    
    def calculate_centered_geometry(self, width: int, height: int) -> str:
        """Calculate geometry string to center window on screen.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            
        Returns:
            str: Geometry string in format 'widthxheight+x+y'
        """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        return f'{width}x{height}+{x}+{y}'

    def change_icon(self, mode: str):
        """Change the application icon.
        
        Args:
            mode: The mode indicating which icon to use ("light" or other)
        """
        if mode == "light":
            self.current_icon = self.dark_logo_path
        else:
            self.current_icon = self.light_logo_path

        try:
            self.iconbitmap(self.current_icon)
        except:
            print(f"Warning: Unable to set application icon from {self.current_icon}")

if __name__ == "__main__":
    app = App()
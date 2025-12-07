from tkinter import *
from tkinter.ttk import *
import customtkinter as ctk
from pages.home_page import HomePage
from pages.login_page import LoginPage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Paragon Apartment Management Portal")
        width = 1000
        height = 650
        self.geometry(self.calculate_centered_geometry(width, height))
        
        # Container to hold all frames
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Get login credentials
        username, password, user_type = self.get_login_details()
        if user_type is None:  # Login was cancelled
            return

        # Open home page with credentials
        self.open_page("HomePage", parent=container, controller=self, user_type=user_type)
        self.mainloop()

    def open_page(self, page_name, **kwargs):
        if page_name == "HomePage":
            home_page = HomePage(kwargs.get("parent"), kwargs.get("controller"), kwargs.get("user_type"))
            home_page.grid(row=0, column=0, sticky="nsew")
            home_page.tkraise()
            return home_page
        elif page_name == "LoginPage":
            login_page = LoginPage(kwargs.get("controller"))
            return login_page
    
    def get_login_details(self):
        # Open login page and wait for it to close
        login_page = self.open_page("LoginPage", controller=self)
        self.wait_window(login_page)  # Wait for login window to close

        # Get credentials from login page
        if hasattr(login_page, 'user_type'):
            return login_page.username, login_page.password, login_page.user_type
        else:
            # User closed login without logging in
            self.destroy()
            return None, None, None

    def logout(self):
        self.destroy()  # Close current app
        App()  # Create new app instance (will show login again)
    
    def calculate_centered_geometry(self, width: int, height: int) -> str:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        return f'{width}x{height}+{x}+{y}'

if __name__ == "__main__":
    app = App()
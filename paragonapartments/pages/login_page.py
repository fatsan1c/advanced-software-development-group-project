from tkinter import *
from tkinter.ttk import *
import customtkinter as ctk

class LoginPage(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
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
        inner_frame = ctk.CTkFrame(container, fg_color="transparent")
        inner_frame.place(relx=0.5, rely=0.54, anchor="center")
        
        ctk.CTkLabel(container, text="Paragon Apartments", font=("Arial", 24)).pack(pady=30)
        ctk.CTkLabel(inner_frame, text="Login", font=("Arial", 18)).pack(pady=(0, 40))
        
        self.username_entry = ctk.CTkEntry(inner_frame, placeholder_text="Username", font=("Arial", 14))
        self.username_entry.pack(pady=(0, 12))
        self.password_entry = ctk.CTkEntry(inner_frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=(0, 12))
        ctk.CTkButton(inner_frame, text="Login",
             command=lambda: self.authenticate(inner_frame, username=self.username_entry.get(), password=self.password_entry.get())).pack()
    
    def authenticate(self, container,username: str, password: str) -> bool:
        if username != None and password == "123":
            print("Login successful")
            self.complete_login(username)
        else:
            if not hasattr(self, 'error_label'):
                self.error_label = ctk.CTkLabel(container, text="Invalid credentials, please try again.", text_color="red")
            self.error_label.pack()
            print("Login failed (use admin/123)")
            return False

    def complete_login(self, user_type: str):
        # Store the credentials
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.user_type = user_type
        self.destroy()  # Close login window, returns to main app
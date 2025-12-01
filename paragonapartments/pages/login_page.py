from tkinter import *
from tkinter.ttk import *
import customtkinter as ctk
from pages.home_page import HomePage

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.parent = parent
        
         # Centered content wrapper
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(expand=True)

        ctk.CTkLabel(self.content, text="Login Page").pack(pady=(0, 12))
        self.username_entry = ctk.CTkEntry(self.content, placeholder_text="Username")
        self.username_entry.pack(pady=(0, 12))
        self.password_entry = ctk.CTkEntry(self.content, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=(0, 12))
        ctk.CTkButton(self.content, text="Login",
             command=lambda: self.authenticate(username=self.username_entry.get(), password=self.password_entry.get())).pack()
        
    def authenticate(self, username: str, password: str) -> bool:
        if username == "admin" and password == "123":
            print("Login successful")
            self.complete_login("admin")
        else:
            if not hasattr(self, 'error_label'):
                self.error_label = ctk.CTkLabel(self.content, text="Invalid credentials, please try again.", text_color="red")
            self.error_label.pack()
            print("Login failed (use admin/123)")
            return False

    def complete_login(self, user_type: str):
        home_page = HomePage(self.parent, self.controller, user_type)
        home_page.grid(row=0, column=0, sticky="nsew")
        home_page.tkraise()
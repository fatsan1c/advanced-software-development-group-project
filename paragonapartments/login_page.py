from tkinter import *
from tkinter.ttk import *
import customtkinter as ctk

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
         # Centered content wrapper
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True)

        ctk.CTkLabel(content, text="Login Page").pack(pady=(0, 12))
        ctk.CTkEntry(content, placeholder_text="Username").pack(pady=(0, 12))
        ctk.CTkEntry(content, placeholder_text="Password", show="*").pack(pady=(0, 12))
        ctk.CTkButton(content, text="Login",
             command=lambda: controller.show_frame("HomePage")).pack()
     
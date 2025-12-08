from tkinter import *
from tkinter.ttk import *
from pathlib import Path
from PIL import Image
import customtkinter as ctk

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller, user):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.controller = controller
        self.user = user

        # Resolve icons path relative to this file
        here = Path(__file__).parent  # paragonapartments/pages
        icons_dir = here.parent / "icons"  # paragonapartments/icons

        self.theme_icon = ctk.CTkImage(
            light_image=Image.open(icons_dir / "light_icon.png"),
            dark_image=Image.open(icons_dir / "dark_icon.png"),
            size=(50, 27.5)
        )

        # Centered content wrapper
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True)

        self.homepage_content(content)
    
    def homepage_content(self, container):
        ctk.CTkLabel(container, text="Paragon Apartments Home", font=("Arial", 24)).pack(pady=20)

        ctk.CTkLabel(container, text="Welcome, "+ self.user.role + "!").pack(pady=(0,12))

        def logout():
            self.controller.logout()  # Restart the app with login

        ctk.CTkButton(container, text="Logout", 
               command=logout).pack()
                
        def toggle_theme():
            mode = ctk.get_appearance_mode()  # "Light" or "Dark"
            ctk.set_appearance_mode("dark" if mode == "Light" else "light")
            theme_button.configure(hover_color=("gray12" if mode == "Light" else "gray93"))

        theme_button = ctk.CTkButton(
            self,
            image=self.theme_icon,
            text="",
            width=50,
            height=25.5,
            fg_color="transparent",
            hover_color="gray12",
            command=toggle_theme
        )
        theme_button.pack(side="bottom", anchor="sw", padx=10, pady=10)
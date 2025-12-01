from tkinter import *
from tkinter.ttk import *
import customtkinter as ctk
from PIL import Image

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Centered content wrapper
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True)

        ctk.CTkLabel(content, text="Home Page").pack(pady=(0,12))
        ctk.CTkButton(content, text="Logout", 
               command=lambda: controller.show_frame("LoginPage")).pack()
                
        self.theme_icon = ctk.CTkImage(
            light_image=Image.open("icons/light_icon.png"),
            dark_image=Image.open("icons/dark_icon.png"),
            size=(50, 27.5)
        )

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
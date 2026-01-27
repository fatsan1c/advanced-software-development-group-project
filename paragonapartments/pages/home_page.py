from pathlib import Path
from PIL import Image
import customtkinter as ctk
from user import User

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller, user : User):
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

        user.load_homepage_content(self)
    
    def close_page(self):
        """Close the home page frame and return to login."""
        self.destroy()
        # Notify controller to handle page transition
        self.controller.handle_logout()
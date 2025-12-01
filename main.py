from tkinter import *
from tkinter.ttk import *
import customtkinter as ctk
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Paragon Apartment Management Portal")
        self.geometry("700x500")
        
        # Container to hold all frames
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        # Create all pages
        for F in (LoginPage, HomePage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(LoginPage)
    
    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()

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
             command=lambda: controller.show_frame(HomePage)).pack()
        

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Centered content wrapper
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True)

        ctk.CTkLabel(content, text="Home Page").pack(pady=(0,12))
        ctk.CTkButton(content, text="Logout", 
               command=lambda: controller.show_frame(LoginPage)).pack()
                
        # 1) Build an icon (use separate light/dark images if you have them)
        self.theme_icon = ctk.CTkImage(
            light_image=Image.open("light_icon.png"),
            dark_image=Image.open("dark_icon.png"),
            size=(50, 27.5)
        )

        # 2) Toggle function
        def toggle_theme():
            mode = ctk.get_appearance_mode()  # "Light" or "Dark"
            ctk.set_appearance_mode("dark" if mode == "Light" else "light")
            theme_button.configure(hover_color=("gray12" if mode == "Light" else "gray93"))

        # 3) Button: image object, no text, bottom-right
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

        print(theme_button)

if __name__ == "__main__":
    app = App()
    app.mainloop()
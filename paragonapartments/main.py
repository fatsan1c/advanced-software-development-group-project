from tkinter import *
from tkinter.ttk import *
import customtkinter as ctk
from pages.home_page import HomePage
from pages.login_page import LoginPage

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
        
        login_page = LoginPage(container, self)
        login_page.grid(row=0, column=0, sticky="nsew")
        login_page.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
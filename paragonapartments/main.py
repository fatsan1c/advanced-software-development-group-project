from tkinter import *
from tkinter.ttk import *
import customtkinter as ctk
from pages.home_page import HomePage
from pages.login_page import LoginPage

class App(ctk.CTk):
    def __init__(self, pages):
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
        for F in pages:
            frame = F(container, self)
            # store by class name to avoid circular imports in page files
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # show first page by name
        self.show_frame(pages[0].__name__)
    
    def show_frame(self, name: str):
        frame = self.frames[name]
        frame.tkraise()

if __name__ == "__main__":
    app = App((LoginPage, HomePage))
    app.mainloop()
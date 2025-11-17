from tkinter import *
from tkinter.ttk import *

from tkinter import *
from tkinter.ttk import *

# Class for creating a new window
class NewWindow(Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("New Window")
        self.geometry("250x150")

        Label(self, text="This is a new window").pack(pady=20)

# Create the main window
master = Tk()
master.geometry("300x200")
master.title("Systems Development Project")

Label(master, text="This is the main window").pack(pady=10)

# Create a button to open the new window using the class
btn = Button(master, text="Open New Window")
btn2 = Button(master, text="This Button does nothing")
btn2.place(x=100, y=100)
btn.bind("<Button>", lambda e: NewWindow(master)) 

btn.pack(pady=10)

# Run the Tkinter event loop
master.mainloop()
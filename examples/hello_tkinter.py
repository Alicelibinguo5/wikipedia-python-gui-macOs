import tkinter as tk
from tkinter import messagebox

# Create main window
root = tk.Tk()
root.title("Simple GUI App")
root.geometry("300x200")

# Function to handle button click
def greet():
    name = name_entry.get()
    messagebox.showinfo("Greeting", f"Hello, {name}!")

# Label
label = tk.Label(root, text="Enter your name:")
label.pack(pady=10)

# Entry box
name_entry = tk.Entry(root)
name_entry.pack(pady=5)

# Button
greet_button = tk.Button(root, text="Greet", command=greet)
greet_button.pack(pady=10)

# Run the app
root.mainloop()
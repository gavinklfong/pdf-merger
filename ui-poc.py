import tkinter as tk
from tkinter import messagebox


def show_message():
    name = name_entry.get().strip()
    if not name:
        messagebox.showwarning("Input Required", "Please enter your name.")
        return
    result_label.config(text=f"Hello, {name}!")


# Create main window
root = tk.Tk()
root.title("Sample Python GUI - Tkinter")
root.geometry("400x200")
root.resizable(False, False)

# Title label
title_label = tk.Label(root, text="Welcome", font=("Arial", 16))
title_label.pack(pady=10)

# Entry field
name_entry = tk.Entry(root, width=30)
name_entry.pack(pady=5)
name_entry.insert(0, "Enter your name")

# Button
submit_button = tk.Button(root, text="Submit", command=show_message)
submit_button.pack(pady=10)

# Result label
result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=5)

# Exit button
exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=10)

# Run the application
root.mainloop()

import tkinter as tk
from tkinter import ttk


def main():
    root = tk.Tk()
    root.title("Greeting Demo")
    root.geometry("350x220")

    # Main container
    container = ttk.Frame(root)
    container.pack(expand=True, fill="both")

    # Welcome label (full width, left-aligned)
    welcome_label = ttk.Label(
        container,
        text="Welcome",
        font=("Arial", 20, "bold"),
        anchor="w"
    )
    welcome_label.pack(fill="x", padx=20, pady=(10, 10))

    # Text box with prefill (full width, left-aligned)
    text_var = tk.StringVar(value="World")
    text_entry = ttk.Entry(
        container,
        textvariable=text_var,
        font=("Arial", 14),
        justify="left"
    )
    text_entry.pack(fill="x", padx=20, pady=(0, 10))

    # Submit button (full width)
    submit_button = ttk.Button(container, text="Submit")
    submit_button.pack(fill="x", padx=20, pady=(0, 10))

    # Output label (full width, left-aligned)
    output_label = ttk.Label(
        container,
        text="",
        font=("Arial", 16),
        anchor="w"
    )
    output_label.pack(fill="x", padx=20)

    def on_submit():
        name = text_var.get().strip()
        output_label.config(text=f"Hello, {name}")

    submit_button.config(command=on_submit)

    root.mainloop()


if __name__ == "__main__":
    main()

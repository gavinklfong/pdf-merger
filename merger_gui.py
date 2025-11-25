import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, END
from PyPDF2 import PdfMerger

class PDFMergerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger")
        self.root.geometry("500x350")

        # Listbox to show selected PDF files
        self.listbox = Listbox(root, width=60, height=12)
        self.listbox.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Add PDFs", width=15, command=self.add_pdfs).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove Selected", width=15, command=self.remove_selected).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Merge PDFs", width=15, command=self.merge_pdfs).grid(row=0, column=2, padx=5)

    def add_pdfs(self):
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")]
        )
        for f in files:
            self.listbox.insert(END, f)

    def remove_selected(self):
        selected = self.listbox.curselection()
        for index in reversed(selected):  # remove from bottom to avoid index shift
            self.listbox.delete(index)

    def merge_pdfs(self):
        files = self.listbox.get(0, END)
        if not files:
            messagebox.showerror("Error", "No PDF files selected.")
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save merged PDF as"
        )

        if not output_file:
            return

        try:
            merger = PdfMerger()
            for pdf in files:
                merger.append(pdf)
            merger.write(output_file)
            merger.close()

            messagebox.showinfo("Success", f"Merged PDF saved:\n{output_file}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerGUI(root)
    root.mainloop()

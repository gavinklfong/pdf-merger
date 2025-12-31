import os
import sys
import subprocess
from PyQt6.QtWidgets import QFileDialog, QMessageBox


class UIActions:
    """
    A controller class that contains all UI event handlers.
    The main window delegates actions to this class.
    """

    def __init__(self, window):
        self.window = window
        self.model = window.model
        self.table = window.table

    # ---------------------------------------------------------
    # Add rows
    # ---------------------------------------------------------
    def add_pdf_row(self, path):
        if not os.path.isfile(path):
            QMessageBox.warning(self.window, "File Missing", f"File not found:\n{path}")
            return

        self.model.add_file(path)

    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self.window,
            "Select PDF or Image Files",
            "",
            "PDF and Images (*.pdf *.jpg *.jpeg *.png *.bmp *.tiff *.webp)"
        )
        for f in files:
            self.add_pdf_row(f)

    def remove_all_pdfs(self):
        self.model.clear()

    # ---------------------------------------------------------
    # Drag & Drop support
    # ---------------------------------------------------------
    def handle_drop(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")):
                self.add_pdf_row(path)
            else:
                QMessageBox.warning(self.window, "Invalid File", f"Not a supported file:\n{path}")

    # ---------------------------------------------------------
    # Row helpers
    # ---------------------------------------------------------
    def row_from_sender(self, sender):
        if sender is None:
            return -1

        parent_widget = sender.parent()
        if parent_widget is None:
            return -1

        index = self.table.indexAt(parent_widget.pos())
        return index.row()

    # ---------------------------------------------------------
    # Button handlers
    # ---------------------------------------------------------
    def on_remove_clicked(self):
        row = self.row_from_sender(self.window.sender())
        if row >= 0:
            self.model.remove_row(row)

    def on_up_clicked(self):
        row = self.row_from_sender(self.window.sender())
        if row > 0:
            self.model.move_up(row)

    def on_down_clicked(self):
        row = self.row_from_sender(self.window.sender())
        if 0 <= row < self.model.rowCount() - 1:
            self.model.move_down(row)

    def on_view_clicked(self):
        row = self.row_from_sender(self.window.sender())
        if row >= 0:
            path = self.model.get_path(row)
            if path:
                self.open_file(path)

    # ---------------------------------------------------------
    # Merge PDFs
    # ---------------------------------------------------------
    def merge_pdfs(self):
        from pdf_utils import merge_files

        file_paths = self.model.get_paths_in_order()

        if not file_paths:
            QMessageBox.warning(self.window, "No Files", "No files added.")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self.window,
            "Save Merged PDF",
            "merged.pdf",
            "PDF Files (*.pdf)"
        )
        if not output_file:
            return

        try:
            merge_files(file_paths, output_file)
            self.open_file(output_file)

        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Error merging PDFs:\n{e}")

    # ---------------------------------------------------------
    # External viewer
    # ---------------------------------------------------------
    def open_file(self, path):
        try:
            if sys.platform.startswith("darwin"):
                subprocess.run(["open", path])
            elif os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.run(["xdg-open", path])
        except Exception as e:
            QMessageBox.critical(self.window, "Open Error", str(e))

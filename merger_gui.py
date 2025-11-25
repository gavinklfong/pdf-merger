import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton,
    QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyPDF2 import PdfMerger


class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Merger (PyQt6)")
        self.setMinimumSize(600, 400)
        self.setAcceptDrops(True)

        layout = QVBoxLayout()

        # List view for PDF files
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(
            self.list_widget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.list_widget)

        # Buttons
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add PDFs")
        add_btn.clicked.connect(self.add_pdfs)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(remove_btn)

        up_btn = QPushButton("Move Up")
        up_btn.clicked.connect(self.move_up)
        btn_layout.addWidget(up_btn)

        down_btn = QPushButton("Move Down")
        down_btn.clicked.connect(self.move_down)
        btn_layout.addWidget(down_btn)

        merge_btn = QPushButton("Merge PDFs")
        merge_btn.clicked.connect(self.merge_pdfs)
        btn_layout.addWidget(merge_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # Drag & Drop support
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".pdf") and os.path.isfile(path):
                self.list_widget.addItem(path)
            else:
                QMessageBox.warning(self, "Invalid File",
                                    f"Not a PDF: {path}")

    # Add files
    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)")
        for f in files:
            self.list_widget.addItem(f)

    # Remove files
    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            row = self.list_widget.row(item)
            self.list_widget.takeItem(row)

    # Move selected item up
    def move_up(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row - 1, item)
            self.list_widget.setCurrentRow(current_row - 1)

    # Move selected item down
    def move_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row + 1, item)
            self.list_widget.setCurrentRow(current_row + 1)

    # Merge PDFs
    def merge_pdfs(self):
        pdf_paths = [self.list_widget.item(i).text()
                     for i in range(self.list_widget.count())]

        if not pdf_paths:
            QMessageBox.warning(self, "No Files", "No PDFs added.")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "merged.pdf", "PDF Files (*.pdf)")

        if not output_file:
            return

        try:
            merger = PdfMerger()
            for pdf in pdf_paths:
                merger.append(pdf)
            merger.write(output_file)
            merger.close()

            QMessageBox.information(self, "Success",
                                    f"Merged PDF saved:\n{output_file}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error merging PDFs:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec())

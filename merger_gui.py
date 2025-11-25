import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton,
    QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyPDF2 import PdfMerger


class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Merger (External Viewer)")
        self.setMinimumSize(600, 400)
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout()

        # --- PDF File List ---
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(
            self.list_widget.SelectionMode.ExtendedSelection)
        main_layout.addWidget(self.list_widget)

        # --- Buttons ---
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

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    # --- Drag & Drop ---
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

    # --- File list actions ---
    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)")
        for f in files:
            self.list_widget.addItem(f)

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            row = self.list_widget.row(item)
            self.list_widget.takeItem(row)

    def move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row - 1, item)
            self.list_widget.setCurrentRow(row - 1)

    def move_down(self):
        row = self.list_widget.currentRow()
        if row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row + 1, item)
            self.list_widget.setCurrentRow(row + 1)

    # --- Merge PDFs ---
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

            # --- Launch external PDF viewer ---
            self.open_pdf_external(output_file)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error merging PDFs:\n{e}")

    def open_pdf_external(self, pdf_path):
        if not os.path.exists(pdf_path):
            return

        try:
            if sys.platform.startswith("darwin"):  # macOS
                subprocess.run(["open", pdf_path])
            elif os.name == "nt":  # Windows
                os.startfile(pdf_path)
            elif os.name == "posix":  # Linux / Unix
                subprocess.run(["xdg-open", pdf_path])
            else:
                QMessageBox.information(self, "Notice",
                                        f"Cannot automatically open PDF on this OS: {pdf_path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open PDF:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec())

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QLabel
)
from PyQt6.QtCore import QSize, Qt
from PyPDF2 import PdfMerger


class PDFListItem(QWidget):
    """Custom row widget containing filename + View + Remove buttons."""
    def __init__(self, pdf_path, parent_list):
        super().__init__()
        self.pdf_path = pdf_path
        self.parent_list = parent_list

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)

        self.label = QLabel(os.path.basename(pdf_path))
        layout.addWidget(self.label)

        view_btn = QPushButton("View")
        view_btn.clicked.connect(self.open_pdf)
        view_btn.setFixedWidth(80)
        layout.addWidget(view_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_self)
        remove_btn.setFixedWidth(80)
        layout.addWidget(remove_btn)

        self.setLayout(layout)

    def open_pdf(self):
        """Open PDF using the OS's default PDF viewer."""
        try:
            if sys.platform.startswith("darwin"):
                subprocess.run(["open", self.pdf_path])
            elif os.name == "nt":
                os.startfile(self.pdf_path)
            elif os.name == "posix":
                subprocess.run(["xdg-open", self.pdf_path])
        except Exception as e:
            QMessageBox.critical(self, "Open Error", str(e))

    def remove_self(self):
        """Remove the list item from the QListWidget."""
        for i in range(self.parent_list.count()):
            item = self.parent_list.item(i)
            if self.parent_list.itemWidget(item) is self:
                self.parent_list.takeItem(i)
                break


class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Merger (PyQt6)")
        self.setMinimumSize(650, 450)
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout()

        # QListWidget for holding PDF entries
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(
            QListWidget.DragDropMode.InternalMove
        )
        main_layout.addWidget(self.list_widget)

        # Buttons Layout
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add PDFs")
        add_btn.clicked.connect(self.add_pdfs)
        btn_layout.addWidget(add_btn)

        merge_btn = QPushButton("Merge PDFs")
        merge_btn.clicked.connect(self.merge_pdfs)
        btn_layout.addWidget(merge_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    # ----------------------------------------
    # Add rows
    # ----------------------------------------
    def add_pdf_row(self, path):
        if not os.path.isfile(path):
            QMessageBox.warning(self, "File Missing", f"File not found:\n{path}")
            return

        item = QListWidgetItem()
        item.setSizeHint(QSize(300, 40))

        widget = PDFListItem(path, self.list_widget)

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)"
        )
        for f in files:
            self.add_pdf_row(f)

    # ----------------------------------------
    # Drag & Drop
    # ----------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".pdf"):
                self.add_pdf_row(path)
            else:
                QMessageBox.warning(self, "Invalid File", f"Not a PDF:\n{path}")

    # ----------------------------------------
    # Merge PDFs
    # ----------------------------------------
    def merge_pdfs(self):
        pdf_paths = []

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row_widget = self.list_widget.itemWidget(item)
            pdf_paths.append(row_widget.pdf_path)

        if not pdf_paths:
            QMessageBox.warning(self, "No Files", "Add PDFs before merging.")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "merged.pdf", "PDF Files (*.pdf)"
        )
        if not output_file:
            return

        try:
            merger = PdfMerger()
            for pdf in pdf_paths:
                merger.append(pdf)
            merger.write(output_file)
            merger.close()

            QMessageBox.information(
                self, "Success", f"Merged PDF saved to:\n{output_file}"
            )

            self.open_pdf_external(output_file)

        except Exception as e:
            QMessageBox.critical(self, "Merge Error", str(e))

    def open_pdf_external(self, pdf_path):
        """Open merged PDF in external viewer."""
        try:
            if sys.platform.startswith("darwin"):
                subprocess.run(["open", pdf_path])
            elif os.name == "nt":
                os.startfile(pdf_path)
            elif os.name == "posix":
                subprocess.run(["xdg-open", pdf_path])
        except Exception as e:
            QMessageBox.critical(self, "Open Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec())

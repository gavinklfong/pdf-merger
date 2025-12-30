import sys
import os
import subprocess
import tempfile
import img2pdf
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QAbstractItemView, QWidget
)
from PyQt6.QtCore import Qt
from PyPDF2 import PdfMerger
from pdf_utils import merge_files


class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Merger")
        self.setMinimumSize(750, 500)
        self.setAcceptDrops(True)

        layout = QVBoxLayout()

        # Table with 2 columns ("File", "Actions")
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["File", "Actions"])

        # Expand the File column, keep Actions compact
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0,
            self.table.horizontalHeader().ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1,
            self.table.horizontalHeader().ResizeMode.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.table.setDragEnabled(True)
        self.table.setDropIndicatorShown(True)

        # Set table row height
        self.table.verticalHeader().setDefaultSectionSize(40)

        layout.addWidget(self.table)

        # Buttons layout
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add PDFs")
        add_btn.clicked.connect(self.add_pdfs)
        btn_layout.addWidget(add_btn)

        merge_btn = QPushButton("Merge PDFs")
        merge_btn.clicked.connect(self.merge_pdfs)
        btn_layout.addWidget(merge_btn)

        remove_all_btn = QPushButton("Remove All PDFs")
        remove_all_btn.clicked.connect(self.remove_all_pdfs)
        btn_layout.addWidget(remove_all_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # ---------------------------------------------------------
    # Add a new row
    # ---------------------------------------------------------
    def add_pdf_row(self, path):
        if not os.path.isfile(path):
            QMessageBox.warning(self, "File Missing", f"File not found:\n{path}")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        # Column 1: full path
        filename = os.path.basename(path)

        file_item = QTableWidgetItem(filename)
        file_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        # Store full path invisibly
        file_item.setData(Qt.ItemDataRole.UserRole, path)

        self.table.setItem(row, 0, file_item)

        # Column 2: actions (View / Remove)
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(5, 0, 5, 0)

        up_btn = QPushButton("Up")
        up_btn.clicked.connect(self._on_up_clicked)
        action_layout.addWidget(up_btn)

        down_btn = QPushButton("Down")
        down_btn.clicked.connect(self._on_down_clicked)
        action_layout.addWidget(down_btn)

        view_btn = QPushButton("View")
        # view by path stored in the file cell (keeps it correct after reorder)
        view_btn.clicked.connect(self._on_view_clicked)
        action_layout.addWidget(view_btn)

        remove_btn = QPushButton("Remove")
        # remove uses sender to find which row to delete
        remove_btn.clicked.connect(self._on_remove_clicked)
        action_layout.addWidget(remove_btn)

        action_widget = QWidget()
        action_widget.setLayout(action_layout)
        self.table.setCellWidget(row, 1, action_widget)

    # ---------------------------------------------------------
    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)"
        )
        for f in files:
            self.add_pdf_row(f)


    def remove_all_pdfs(self):
        self.table.setRowCount(0)

    # ---------------------------------------------------------
    # Drag & Drop support
    # ---------------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
                self.add_pdf_row(path)
            else:
                QMessageBox.warning(self, "Invalid File", f"Not a PDF or image file:\n{path}")

    # ---------------------------------------------------------
    # Remove handler (find row dynamically)
    # ---------------------------------------------------------
    def _on_remove_clicked(self):
        sender = self.sender()  # the QPushButton
        if sender is None:
            return

        parent_widget = sender.parent()  # the QWidget that was set as cell widget
        if parent_widget is None:
            return

        # find which row has this cell widget
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 1) is parent_widget:
                self.table.removeRow(row)
                return
            
    # ---------------------------------------------------------
    # Swap up position handler (find row dynamically)
    # ---------------------------------------------------------
    def _on_up_clicked(self):
        sender = self.sender()  # the QPushButton
        if sender is None:
            return

        parent_widget = sender.parent()  # the QWidget that was set as cell widget
        if parent_widget is None:
            return

        # find which row has this cell widget
        current_row = -1
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 1) is parent_widget:
                current_row = row
                break
        
        if current_row > 0:
            previous_row = current_row - 1
            current_path = self.table.item(current_row, 0).text()
            previous_path = self.table.item(previous_row, 0).text()
            self.table.item(current_row, 0).setText(previous_path)
            self.table.item(previous_row, 0).setText(current_path)


    def _on_down_clicked(self):
        sender = self.sender()  # the QPushButton
        if sender is None:
            return

        parent_widget = sender.parent()  # the QWidget that was set as cell widget
        if parent_widget is None:
            return

        # find which row has this cell widget
        current_row = -1
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 1) is parent_widget:
                current_row = row
                break
        
        if current_row < self.table.rowCount() - 1:
            next_row = current_row + 1
            current_path = self.table.item(current_row, 0).text()
            next_path = self.table.item(next_row, 0).text()
            self.table.item(current_row, 0).setText(next_path)
            self.table.item(next_row, 0).setText(current_path)

    # ---------------------------------------------------------
    # View handler (open file from the File column of the row)
    # ---------------------------------------------------------
    def _on_view_clicked(self):
        sender = self.sender()
        if sender is None:
            return

        parent_widget = sender.parent()
        if parent_widget is None:
            return

        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 1) is parent_widget:
                item = self.table.item(row, 0)
                if item:
                    path = item.data(Qt.ItemDataRole.UserRole)
                    self.open_pdf(path)
                return

    # ---------------------------------------------------------
    # Merge PDFs
    # ---------------------------------------------------------
    def merge_pdfs(self):
        pdf_paths = []

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                pdf_paths.append(item.data(Qt.ItemDataRole.UserRole))

        if not pdf_paths:
            QMessageBox.warning(self, "No Files", "No files added.")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "merged.pdf", "PDF Files (*.pdf)"
        )
        if not output_file:
            return

        try:
            merge_files(pdf_paths, output_file)
            self.open_pdf(output_file)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error merging PDFs:\n{e}")



    # ---------------------------------------------------------
    # External PDF viewer
    # ---------------------------------------------------------
    def open_pdf(self, path):
        try:
            if sys.platform.startswith("darwin"):
                subprocess.run(["open", path])
            elif os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.run(["xdg-open", path])
        except Exception as e:
            QMessageBox.critical(self, "Open Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec())

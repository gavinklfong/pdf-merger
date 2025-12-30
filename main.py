import sys
import os
import subprocess

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QAbstractItemView
)
from PyQt6.QtCore import Qt

from pdf_utils import merge_files


class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()

        # Load UI from .ui file
        uic.loadUi("pdf_merger.ui", self)

        # Ensure main window properties
        self.setWindowTitle("PDF Merger")
        self.setMinimumSize(750, 500)
        self.setAcceptDrops(True)

        # The .ui defines a QTableWidget named "table"
        self._configure_table()

        # Connect buttons (names from .ui: add_btn, merge_btn, remove_all_btn)
        self.add_btn.clicked.connect(self.add_pdfs)
        self.merge_btn.clicked.connect(self.merge_pdfs)
        self.remove_all_btn.clicked.connect(self.remove_all_pdfs)

    # ---------------------------------------------------------
    # Table configuration
    # ---------------------------------------------------------
    def _configure_table(self):
        # Defensive: ensure 2 columns and labels
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["File", "Actions"])

        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.table.setDragEnabled(True)
        self.table.setDropIndicatorShown(True)

        self.table.verticalHeader().setDefaultSectionSize(40)

    # ---------------------------------------------------------
    # Add a new row
    # ---------------------------------------------------------
    def add_pdf_row(self, path):
        if not os.path.isfile(path):
            QMessageBox.warning(self, "File Missing", f"File not found:\n{path}")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        # Column 0: file name (visible), full path stored in UserRole
        filename = os.path.basename(path)
        file_item = QTableWidgetItem(filename)
        file_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # not editable
        file_item.setData(Qt.ItemDataRole.UserRole, path)
        self.table.setItem(row, 0, file_item)

        # Column 1: actions (Up / Down / View / Remove)
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(5, 0, 5, 0)

        up_btn = QPushButton("Up")
        up_btn.clicked.connect(self._on_up_clicked)
        action_layout.addWidget(up_btn)

        down_btn = QPushButton("Down")
        down_btn.clicked.connect(self._on_down_clicked)
        action_layout.addWidget(down_btn)

        view_btn = QPushButton("View")
        view_btn.clicked.connect(self._on_view_clicked)
        action_layout.addWidget(view_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._on_remove_clicked)
        action_layout.addWidget(remove_btn)

        action_widget = QWidget()
        action_widget.setLayout(action_layout)
        self.table.setCellWidget(row, 1, action_widget)

    # ---------------------------------------------------------
    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF or Image Files",
            "",
            "PDF and Images (*.pdf *.jpg *.jpeg *.png *.bmp *.tiff *.webp)"
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
            if path.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")):
                self.add_pdf_row(path)
            else:
                QMessageBox.warning(self, "Invalid File", f"Not a supported file:\n{path}")

    # ---------------------------------------------------------
    # Remove handler (find row dynamically)
    # ---------------------------------------------------------
    def _on_remove_clicked(self):
        sender = self.sender()
        if sender is None:
            return

        parent_widget = sender.parent()
        if parent_widget is None:
            return

        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 1) is parent_widget:
                self.table.removeRow(row)
                return

    # ---------------------------------------------------------
    # Move Up / Down handlers (swap rows)
    # ---------------------------------------------------------
    def _swap_rows(self, row1, row2):
        if not (0 <= row1 < self.table.rowCount() and 0 <= row2 < self.table.rowCount()):
            return

        # Swap the file item
        item1 = self.table.item(row1, 0)
        item2 = self.table.item(row2, 0)

        if not item1 or not item2:
            return

        text1 = item1.text()
        text2 = item2.text()
        path1 = item1.data(Qt.ItemDataRole.UserRole)
        path2 = item2.data(Qt.ItemDataRole.UserRole)

        item1.setText(text2)
        item1.setData(Qt.ItemDataRole.UserRole, path2)

        item2.setText(text1)
        item2.setData(Qt.ItemDataRole.UserRole, path1)

    def _on_up_clicked(self):
        sender = self.sender()
        if sender is None:
            return

        parent_widget = sender.parent()
        if parent_widget is None:
            return

        current_row = -1
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 1) is parent_widget:
                current_row = row
                break

        if current_row > 0:
            self._swap_rows(current_row, current_row - 1)

    def _on_down_clicked(self):
        sender = self.sender()
        if sender is None:
            return

        parent_widget = sender.parent()
        if parent_widget is None:
            return

        current_row = -1
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 1) is parent_widget:
                current_row = row
                break

        if current_row >= 0 and current_row < self.table.rowCount() - 1:
            self._swap_rows(current_row, current_row + 1)

    # ---------------------------------------------------------
    # View handler
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
                    if path:
                        self.open_file(path)
                return

    # ---------------------------------------------------------
    # Merge PDFs
    # ---------------------------------------------------------
    def merge_pdfs(self):
        file_paths = []

        # Collect file paths from the table
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                path = item.data(Qt.ItemDataRole.UserRole)
                if path:
                    file_paths.append(path)

        if not file_paths:
            QMessageBox.warning(self, "No Files", "No files added.")
            return

        # Ask user where to save the merged PDF
        output_file, _ = QFileDialog.getSaveFileName(
            self,
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
            QMessageBox.critical(self, "Error", f"Error merging PDFs:\n{e}")

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
            QMessageBox.critical(self, "Open Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec())

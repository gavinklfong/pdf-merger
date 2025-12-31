import sys
import os
import subprocess

from PyQt6 import uic 
from PyQt6.QtWidgets import ( 
    QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QAbstractItemView, QMenuBar, QMenu ) 
from PyQt6.QtGui import QAction 

from logic.pdf_utils import merge_files
from models.file_list_model import FileListModel
from views.file_table_view import FileTableView


class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()

        # Load UI from .ui file
        uic.loadUi("ui/pdf_merger.ui", self)

        # Replace the placeholder table (QTableWidget from .ui) with FileTableView
        self._setup_table_view()

        # Setup model
        self.model = FileListModel(self)
        self.table.setModel(self.model)

        # Menu bar
        self._create_menu_bar()

        # Configure columns/visual behavior
        self._configure_table()

        # Connect buttons from UI
        self.add_btn.clicked.connect(self.add_pdfs)
        self.merge_btn.clicked.connect(self.merge_pdfs)
        self.remove_all_btn.clicked.connect(self.remove_all_pdfs)

        # React to model changes to rebuild action widgets
        self.model.rowsInserted.connect(self._rebuild_action_widgets)
        self.model.rowsRemoved.connect(self._rebuild_action_widgets)
        self.model.modelReset.connect(self._rebuild_action_widgets)
        self.model.rowsMoved.connect(self._rebuild_action_widgets)

        self.setAcceptDrops(True)
        self.setWindowTitle("PDF Merger")
        self.setMinimumSize(750, 500)

    # ---------------------------------------------------------
    # Replace table from .ui with FileTableView
    # ---------------------------------------------------------
    def _setup_table_view(self):
        # The .ui has a widget named "table", likely QTableWidget
        old_table = self.table

        # Create our custom view
        self.table = FileTableView(self)

        # Replace in layout
        parent_layout = old_table.parent().layout()
        index = parent_layout.indexOf(old_table)
        parent_layout.removeWidget(old_table)
        old_table.deleteLater()
        parent_layout.insertWidget(index, self.table)

    # ---------------------------------------------------------
    # Menu bar
    # ---------------------------------------------------------
    def _create_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        # Top-level layout from .ui is assumed to be a QVBoxLayout
        self.layout().setMenuBar(self.menu_bar)

        settings_menu = QMenu("Settings", self)
        self.menu_bar.addMenu(settings_menu)

        settings_action = QAction("Preferences", self)
        settings_action.triggered.connect(self._open_settings)
        settings_menu.addAction(settings_action)

    def _open_settings(self):
        QMessageBox.information(self, "Settings", "Settings dialog goes here.")

    # ---------------------------------------------------------
    # Table configuration
    # ---------------------------------------------------------
    def _configure_table(self):
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)

        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    # ---------------------------------------------------------
    # Action widgets (Up / Down / View / Remove) per row
    # ---------------------------------------------------------
    def _create_action_widget_for_row(self, row):
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

        index = self.model.index(row, 1)
        self.table.setIndexWidget(index, action_widget)

    def _rebuild_action_widgets(self):
        # Clear existing index widgets (Qt handles deletion)
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 1)
            self.table.setIndexWidget(index, None)

        # Recreate them
        for row in range(self.model.rowCount()):
            self._create_action_widget_for_row(row)

    # ---------------------------------------------------------
    # Add rows
    # ---------------------------------------------------------
    def add_pdf_row(self, path):
        if not os.path.isfile(path):
            QMessageBox.warning(self, "File Missing", f"File not found:\n{path}")
            return

        self.model.add_file(path)
        # The rowsInserted signal will rebuild action widgets

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
        self.model.clear()

    # ---------------------------------------------------------
    # Drag & Drop support (for files from OS)
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
    # Row helpers: find row from action button sender
    # ---------------------------------------------------------
    def _row_from_sender(self, sender):
        if sender is None:
            return -1

        parent_widget = sender.parent()
        if parent_widget is None:
            return -1

        # Use indexAt with the parent's position
        index = self.table.indexAt(parent_widget.pos())
        return index.row()

    # ---------------------------------------------------------
    # Remove handler
    # ---------------------------------------------------------
    def _on_remove_clicked(self):
        sender = self.sender()
        row = self._row_from_sender(sender)
        if row < 0:
            return
        self.model.remove_row(row)

    # ---------------------------------------------------------
    # Move Up / Down handlers
    # ---------------------------------------------------------
    def _on_up_clicked(self):
        sender = self.sender()
        row = self._row_from_sender(sender)
        if row <= 0:
            return
        self.model.move_up(row)

    def _on_down_clicked(self):
        sender = self.sender()
        row = self._row_from_sender(sender)
        if row < 0 or row >= self.model.rowCount() - 1:
            return
        self.model.move_down(row)

    # ---------------------------------------------------------
    # View handler
    # ---------------------------------------------------------
    def _on_view_clicked(self):
        sender = self.sender()
        row = self._row_from_sender(sender)
        if row < 0:
            return

        path = self.model.get_path(row)
        if path:
            self.open_file(path)

    # ---------------------------------------------------------
    # Merge PDFs
    # ---------------------------------------------------------
    def merge_pdfs(self):
        file_paths = self.model.get_paths_in_order()

        if not file_paths:
            QMessageBox.warning(self, "No Files", "No files added.")
            return

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

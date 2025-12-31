import sys
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QWidget, QAbstractItemView
)

from models.file_list_model import FileListModel
from views.file_table_view import FileTableView
from controllers.ui_actions import UIActions


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

        # Controller for all UI actions
        self.actions = UIActions(self)

        # Configure table appearance
        self._configure_table()

        # Connect top‑level UI buttons
        self.add_btn.clicked.connect(self.actions.add_pdfs)
        self.merge_btn.clicked.connect(self.actions.merge_pdfs)
        self.remove_all_btn.clicked.connect(self.actions.remove_all_pdfs)

        # Connect menu actions defined in the .ui file
        self.actionPreferences.triggered.connect(self._open_settings)

        # Rebuild action widgets whenever the model changes
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
    # Rebuild action widgets (delegates to FileTableView)
    # ---------------------------------------------------------
    def _rebuild_action_widgets(self):
        # Clear existing widgets
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 1)
            self.table.setIndexWidget(index, None)

        # Recreate using FileTableView method
        for row in range(self.model.rowCount()):
            self.table.create_action_widget(row, self.actions)

    # ---------------------------------------------------------
    # Menu action
    # ---------------------------------------------------------
    def _open_settings(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Settings", "Settings dialog goes here.")

    # ---------------------------------------------------------
    # Drag & Drop support (delegated to controller)
    # ---------------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.actions.handle_drop(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec())

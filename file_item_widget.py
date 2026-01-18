import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QStyle
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal


class FileItemWidget(QWidget):
    viewRequested = Signal()
    deleteRequested = Signal()

    def __init__(self, filePath):
        super().__init__()

        self.filePath = filePath

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = QLabel(os.path.basename(filePath))

        # --- View button (icon only) ---
        btn_view = QPushButton()
        view_icon = self.style().standardIcon(QStyle.SP_FileIcon)
        btn_view.setIcon(view_icon)
        btn_view.setToolTip("View file")
        btn_view.setFixedSize(28, 28)

        # --- Delete button (icon only) ---
        btn_delete = QPushButton()
        delete_icon = self.style().standardIcon(QStyle.SP_TrashIcon)
        btn_delete.setIcon(delete_icon)
        btn_delete.setToolTip("Delete file")
        btn_delete.setFixedSize(28, 28)

        # Store references for tests 
        self.btn_view = btn_view 
        self.btn_delete = btn_delete

        # Connect signals
        btn_view.clicked.connect(self.viewRequested)
        btn_delete.clicked.connect(self.deleteRequested)

        # Layout
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(btn_view)
        layout.addWidget(btn_delete)

        self.setMouseTracking(True)
        self.setToolTip(self.filePath)

import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Signal

# ---------------------------------------------------------
#  Custom widget for each row (filename + buttons)
# ---------------------------------------------------------
class FileItemWidget(QWidget):
    viewRequested = Signal() 
    deleteRequested = Signal()

    def __init__(self, filePath):
        super().__init__()

        self.filePath = filePath

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = QLabel(os.path.basename(filePath))
        btn_view = QPushButton("View")
        btn_delete = QPushButton("Delete")

        btn_view.clicked.connect(self.viewRequested) 
        btn_delete.clicked.connect(self.deleteRequested)

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(btn_view)
        layout.addWidget(btn_delete)

        self.setMouseTracking(True)

        self.setToolTip(self.filePath)
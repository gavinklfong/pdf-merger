import os
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import Qt


# ---------------------------------------------------------
#  Custom widget for each row (filename + buttons)
# ---------------------------------------------------------
class FileItemWidget(QWidget):
    def __init__(self, filename, on_view, on_delete):
        super().__init__()

        self.filename = filename

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = QLabel(filename)
        btn_view = QPushButton("View")
        btn_delete = QPushButton("Delete")

        btn_view.clicked.connect(lambda: on_view(self.filename))
        btn_delete.clicked.connect(lambda: on_delete(self.filename))

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(btn_view)
        layout.addWidget(btn_delete)

        self.setMouseTracking(True)


# ---------------------------------------------------------
#  Custom QListWidget with:
#   - internal reordering
#   - external file drop
#   - auto-scroll
#   - drop indicator
#   - hover highlight
# ---------------------------------------------------------
class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Internal drag reorder
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.InternalMove)

        # Auto-scroll
        self.setAutoScroll(True)
        self.setAutoScrollMargin(30)

        # Drop indicator
        self.setDropIndicatorShown(True)

        # Hover highlight
        self.setMouseTracking(True)
        self.setStyleSheet("""
            QListWidget::item:hover {
                background: #e6f2ff;
                border: 1px solid #99ccff;
            }
            QListWidget::item:selected {
                background: #cce6ff;
                border: 1px solid #66b3ff;
            }
        """)

    def addFileItem(self, path):
        filename = os.path.basename(path)

        widget = FileItemWidget(
            filename,
            on_view=self.viewFileItem,
            on_delete=self.removeFileItemByFilename
        )

        # IMPORTANT:
        # - item text must contain filename (for drag pixmap)
        # - foreground transparent prevents overlap
        item = QListWidgetItem(filename)
        item.setForeground(Qt.transparent)
        item.setSizeHint(widget.sizeHint())

        self.addItem(item)
        self.setItemWidget(item, widget)

    def removeFileItemByFilename(self, filename):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget and widget.filename == filename:
                self.takeItem(i)
                widget.deleteLater()
                del item
                return

    def viewFileItem(self, filename):
        print("View:", filename)

    # -----------------------------------------------------
    #  External file drop support
    # -----------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path:
                    self.handleDroppedFile(path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    # This will be overridden by MainWindow
    def handleDroppedFile(self, path):
        print("Dropped:", path)
        self.addFileItem(path)

# ---------------------------------------------------------
#  Main Window
# ---------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.list = FileListWidget()

        layout = QVBoxLayout(self)
        layout.addWidget(self.list)

        # Example items
        for f in ["report.pdf", "image.png", "notes.txt"]:
            self.list.addFileItem(f)

    # -----------------------------------------------------
    #  Callbacks
    # -----------------------------------------------------
    def view_file(self, filename):
        print("View:", filename)

# ---------------------------------------------------------
#  Run App
# ---------------------------------------------------------
app = QApplication(sys.argv)
w = MainWindow()
w.resize(500, 300)
w.show()
app.exec()

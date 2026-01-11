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


# ---------------------------------------------------------
#  Main Window
# ---------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.list = FileListWidget()
        self.list.handleDroppedFile = self.add_file_item  # override callback

        layout = QVBoxLayout(self)
        layout.addWidget(self.list)

        # Example items
        for f in ["report.pdf", "image.png", "notes.txt"]:
            self.add_file_item(f)

    # -----------------------------------------------------
    #  Add file item (single call)
    # -----------------------------------------------------
    def add_file_item(self, path):
        filename = os.path.basename(path)

        widget = FileItemWidget(
            filename,
            on_view=self.view_file,
            on_delete=self.delete_file
        )

        # IMPORTANT:
        # - item text must contain filename (for drag pixmap)
        # - foreground transparent prevents overlap
        item = QListWidgetItem(filename)
        item.setForeground(Qt.transparent)
        item.setSizeHint(widget.sizeHint())

        self.list.addItem(item)
        self.list.setItemWidget(item, widget)

    # -----------------------------------------------------
    #  Callbacks
    # -----------------------------------------------------
    def view_file(self, filename):
        print("View:", filename)

    def delete_file(self, filename):
        print("Delete:", filename)
        self.remove_by_filename(filename)

    # -----------------------------------------------------
    #  Remove item by filename
    # -----------------------------------------------------
    def remove_by_filename(self, filename):
        for i in range(self.list.count()):
            item = self.list.item(i)
            widget = self.list.itemWidget(item)
            if widget and widget.filename == filename:
                self.list.takeItem(i)
                widget.deleteLater()
                del item
                return


# ---------------------------------------------------------
#  Run App
# ---------------------------------------------------------
app = QApplication(sys.argv)
w = MainWindow()
w.resize(500, 300)
w.show()
app.exec()

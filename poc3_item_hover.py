from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QVBoxLayout
)

from PySide6.QtCore import Qt, QUrl
import sys


class FileDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Enable internal reordering
        self.setAcceptDrops(True) 
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.InternalMove)

        # Enable auto‑scrolling during drag 
        self.setAutoScroll(True)
        self.setAutoScrollMargin(30) # adjust to taste

        # Visual drop indicator
        self.setDropIndicatorShown(True)    

        self.setMouseTracking(True)

        self.setStyleSheet("""
            QListWidget::item:hover {
                background: #e6f2ff;      /* light blue */
                border: 1px solid #99ccff;
            }
            QListWidget::item:selected {
                background: #cce6ff;
                border: 1px solid #66b3ff;
            }
        """)
    

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event) # allow internal drag

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event) # allow internal drag

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path:
                    self.handleDroppedFile(path)
            event.acceptProposedAction()
        else:
            # internal move → let Qt handle it 
            super().dropEvent(event)

    def handleDroppedFile(self, path):
        """Override this in your main window to add the file."""
        print("Dropped:", path)

class FileItemWidget(QWidget):
    def __init__(self, filename, on_view, on_delete):
        super().__init__()

        self.filename = filename

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        label = QLabel(filename)
        btn_view = QPushButton("View")
        btn_delete = QPushButton("Delete")

        btn_view.clicked.connect(lambda: on_view(self.filename))
        btn_delete.clicked.connect(lambda: on_delete(self.filename))

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(btn_view)
        layout.addWidget(btn_delete)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.list = FileDropListWidget()
        self.list.handleDroppedFile = self.add_file_item # override callback
        self.list.setDragEnabled(True) 
        self.list.setAcceptDrops(True) 
        self.list.setDragDropMode(QListWidget.InternalMove)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list)

        # Example items
        for f in ["file1.pdf", "image.png", "notes.txt"]:
            self.add_file_item(f)

    def add_file_item(self, filename):
        item = QListWidgetItem(True)
        widget = FileItemWidget(
            filename,
            on_view=self.view_file,
            on_delete=self.delete_file
        )

        item.setSizeHint(widget.sizeHint())
        self.list.addItem(item)
        self.list.setItemWidget(item, widget)

    def view_file(self, filename):
        print("View:", filename)

    def delete_file(self, filename):
        print("Delete:", filename)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()

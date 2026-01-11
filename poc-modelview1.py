from PySide6.QtCore import (
    Qt, QModelIndex, QAbstractListModel, QSize, Signal
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QListView, QHBoxLayout, QPushButton,
    QLabel, QStyledItemDelegate, QVBoxLayout, QStyle
)
from PySide6.QtGui import QPainter


# -----------------------------
# Model
# -----------------------------
class FileListModel(QAbstractListModel):
    def __init__(self, files=None):
        super().__init__()
        self._files = files or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._files)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._files[index.row()]
        return None

    def removeRow(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        self._files.pop(row)
        self.endRemoveRows()


# -----------------------------
# Editor widget for each row
# -----------------------------
class FileItemWidget(QWidget):
    viewClicked = Signal(int)
    deleteClicked = Signal(int)

    def __init__(self, index, filename):
        super().__init__()
        self.index = index

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = QLabel(filename)
        self.btnView = QPushButton("View")
        self.btnDelete = QPushButton("Delete")

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.btnView)
        layout.addWidget(self.btnDelete)

        self.btnView.clicked.connect(lambda: self.viewClicked.emit(self.index))
        self.btnDelete.clicked.connect(lambda: self.deleteClicked.emit(self.index))

    def sizeHint(self):
        return QSize(300, 36)


# -----------------------------
# Delegate
# -----------------------------
class FileItemDelegate(QStyledItemDelegate):
    viewRequested = Signal(int)
    deleteRequested = Signal(int)

    def paint(self, painter, option, index):
        # Draw hover highlight
        painter.save()
        if option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            painter.fillRect(option.rect, option.palette.base())
        painter.restore()
        # Do NOT draw text — editor widget handles it

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 36)

    def createEditor(self, parent, option, index):
        filename = index.data(Qt.DisplayRole)
        widget = FileItemWidget(index.row(), filename)
        widget.setParent(parent)

        widget.viewClicked.connect(self.viewRequested)
        widget.deleteClicked.connect(self.deleteRequested)

        return widget

    def setEditorData(self, editor, index):
        editor.label.setText(index.data(Qt.DisplayRole))
        editor.index = index.row()

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


# -----------------------------
# Main Window
# -----------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.model = FileListModel([
            "report.pdf",
            "image.png",
            "notes.txt",
            "presentation.pptx"
        ])

        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setMouseTracking(True)  # enable hover
        self.view.setSpacing(2)

        self.view.setMouseTracking(True)
        self.view.viewport().setMouseTracking(True)
        self.view.setAttribute(Qt.WA_Hover, True)
        self.view.viewport().setAttribute(Qt.WA_Hover, True)


        self.delegate = FileItemDelegate()
        self.view.setItemDelegate(self.delegate)

        self.delegate.viewRequested.connect(self.onView)
        self.delegate.deleteRequested.connect(self.onDelete)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)

        # Open persistent editors for all rows
        self.refreshEditors()

    def refreshEditors(self):
        for row in range(self.model.rowCount()):
            index = self.model.index(row)
            self.view.openPersistentEditor(index)

    def onView(self, row):
        print(f"View requested for: {self.model._files[row]}")

    def onDelete(self, row):
        print(f"Delete requested for: {self.model._files[row]}")
        self.model.removeRow(row)
        self.refreshEditors()


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.resize(450, 300)
    w.show()
    app.exec()

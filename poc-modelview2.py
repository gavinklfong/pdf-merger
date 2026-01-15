from PySide6.QtCore import (
    Qt, QModelIndex, QAbstractTableModel, QSize, Signal
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QTableView, QStyledItemDelegate,
    QPushButton, QHBoxLayout, QVBoxLayout, QHeaderView
)


# -----------------------------
# Model with drag & drop support
# -----------------------------
class FileTableModel(QAbstractTableModel):
    def __init__(self, files=None):
        super().__init__()
        self._files = files or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._files)

    def columnCount(self, parent=QModelIndex()):
        return 2  # filename + buttons

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole and index.column() == 0:
            return self._files[index.row()]

        return None

    # -----------------------------
    # Drag/drop support
    # -----------------------------
    def flags(self, index):
        base = super().flags(index)
        if index.isValid():
            return base | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return base | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return ["application/x-row"]

    def mimeData(self, indexes):
        mime = super().mimeData(indexes)
        row = indexes[0].row()
        mime.setData("application/x-row", str(row).encode())
        return mime

    def dropMimeData(self, mime, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return False

        if not mime.hasFormat("application/x-row"):
            return False

        from_row = int(bytes(mime.data("application/x-row")).decode())

        if row == -1:
            row = parent.row()

        return self.moveRows(QModelIndex(), from_row, 1, QModelIndex(), row)

    def moveRows(self, sourceParent, sourceRow, count, destParent, destRow):
        if destRow > sourceRow:
            adjustedDest = destRow - 1
        else:
            adjustedDest = destRow

        if adjustedDest == sourceRow:
            return False

        self.beginMoveRows(QModelIndex(), sourceRow, sourceRow, QModelIndex(), destRow)

        item = self._files.pop(sourceRow)
        self._files.insert(adjustedDest, item)

        self.endMoveRows()
        return True



    # -----------------------------
    # Remove row
    # -----------------------------
    def removeRow(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        self._files.pop(row)
        self.endRemoveRows()


# -----------------------------
# Editor widget for button column
# -----------------------------
class ButtonCell(QWidget):
    viewClicked = Signal(object)
    deleteClicked = Signal(object)

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        self.btnView = QPushButton("View")
        self.btnDelete = QPushButton("Delete")

        layout.addWidget(self.btnView)
        layout.addWidget(self.btnDelete)

    def sizeHint(self):
        return QSize(120, 30)


# -----------------------------
# Delegate for button column
# -----------------------------
class ButtonDelegate(QStyledItemDelegate):
    viewRequested = Signal(int)
    deleteRequested = Signal(int)

    def createEditor(self, parent, option, index):
        editor = ButtonCell()
        editor.setParent(parent)

        # Dynamic row lookup
        editor.btnView.clicked.connect(lambda _, e=editor: self._emitView(e))
        editor.btnDelete.clicked.connect(lambda _, e=editor: self._emitDelete(e))

        return editor

    def _emitView(self, editor):
        table = editor.parent().parent()  # viewport → table
        index = table.indexAt(editor.pos())
        if index.isValid():
            self.viewRequested.emit(index.row())

    def _emitDelete(self, editor):
        table = editor.parent().parent()
        index = table.indexAt(editor.pos())
        if index.isValid():
            self.deleteRequested.emit(index.row())

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


# -----------------------------
# Main Window
# -----------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.model = FileTableModel([
            "report.pdf",
            "image.png",
            "notes.txt",
            "presentation.pptx"
        ])

        self.table = QTableView()
        self.table.setModel(self.model)

        # Hover support
        self.table.setMouseTracking(True)
        self.table.viewport().setMouseTracking(True)
        self.table.setAttribute(Qt.WA_Hover, True)
        self.table.viewport().setAttribute(Qt.WA_Hover, True)

        self.table.setStyleSheet("""
            QTableView::item:hover {
                background-color: #d0e7ff;
            }
        """)

        # Drag & drop
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDragDropMode(QTableView.InternalMove)
        self.table.setDefaultDropAction(Qt.MoveAction)

        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(1, 150)

        # Delegate for button column
        self.delegate = ButtonDelegate()
        self.table.setItemDelegateForColumn(1, self.delegate)

        self.delegate.viewRequested.connect(self.onView)
        self.delegate.deleteRequested.connect(self.onDelete)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

        self.openEditors()

    def openEditors(self):
        # Close old editors
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 1)
            self.table.closePersistentEditor(index)

        # Open new editors
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 1)
            self.table.openPersistentEditor(index)

    def onView(self, row):
        print(f"View requested for: {self.model._files[row]}")

    def onDelete(self, row):
        print(f"Delete requested for: {self.model._files[row]}")
        self.model.removeRow(row)
        self.openEditors()


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.resize(600, 300)
    w.show()
    app.exec()

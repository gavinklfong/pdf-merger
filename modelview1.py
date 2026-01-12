from PySide6.QtCore import (
    Qt, QAbstractListModel, QModelIndex, QMimeData
)
from PySide6.QtWidgets import QApplication, QListView


class ReorderableListModel(QAbstractListModel):
    def __init__(self, items):
        super().__init__()
        self._items = items

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._items[index.row()]

    def flags(self, index):
        default = super().flags(index)
        if index.isValid():
            return default | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return default | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return ["application/x-item"]

    def mimeData(self, indexes):
        mime = QMimeData()
        mime.setData("application/x-item", str(indexes[0].row()).encode())
        return mime

    def dropMimeData(self, mime, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return False

        source_row = int(bytes(mime.data("application/x-item")).decode())

        if row == -1:
            row = self.rowCount()

        self.moveRows(QModelIndex(), source_row, 1, QModelIndex(), row)
        return True

    def moveRows(self, src_parent, src_row, count, dst_parent, dst_row):
        if src_row == dst_row or src_row + 1 == dst_row:
            return False

        self.beginMoveRows(src_parent, src_row, src_row, dst_parent, dst_row)

        item = self._items.pop(src_row)
        if dst_row > src_row:
            dst_row -= 1
        self._items.insert(dst_row, item)

        self.endMoveRows()
        return True


app = QApplication([])
view = QListView()
model = ReorderableListModel(["A", "B", "C", "D"])
view.setModel(model)
view.setDragDropMode(QListView.InternalMove)
view.show()
app.exec()

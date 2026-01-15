
from PySide6.QtWidgets import QApplication, QTableView, QAbstractItemView
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QMimeData, QByteArray


class DragDropTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    # --- Required table model functions ---
    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data[0])

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    # --- Enable dragging & dropping rows ---
    def flags(self, index):
        default = super().flags(index)
        return default | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return ["application/x-row"]

    def mimeData(self, indexes):
        mime = QMimeData()
        row = indexes[0].row()
        mime.setData("application/x-row", QByteArray(str(row).encode()))
        return mime

    def dropMimeData(self, mimeData, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return False

        from_row = int(bytes(mimeData.data("application/x-row")).decode())

        # If row is -1, compute it using parent index
        if row == -1:
            if parent.isValid():
                row = parent.row()
            else:
                # fallback: append at end
                row = self.rowCount()

        # if row > from_row:
        #     row -= 1

        self.beginMoveRows(QModelIndex(), from_row, from_row, QModelIndex(), row)
        self._data.insert(row, self._data.pop(from_row))
        self.endMoveRows()

        return True


# ---------- App Setup ----------
app = QApplication([])

data = [
    ["A", 1],
    ["B", 2],
    ["C", 3],
    ["D", 4],
]

model = DragDropTableModel(data)

view = QTableView()
view.setModel(model)

# Enable row moving
view.setDragDropMode(QAbstractItemView.InternalMove)
view.setDragEnabled(True)
view.setAcceptDrops(True)
view.setDropIndicatorShown(True)
view.setDefaultDropAction(Qt.MoveAction)

view.show()
app.exec()

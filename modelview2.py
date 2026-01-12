from PySide6.QtCore import (
    Qt,
    QAbstractListModel,
    QModelIndex,
    QMimeData,
    QRect,
    QSize,
    Signal,
    QEvent,
)
from PySide6.QtGui import QPainter, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QListView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionButton,
    QWidget,
    QVBoxLayout,
)


# ============================================================
#  MODEL — Reorderable list using moveRows()
# ============================================================
class ReorderableListModel(QAbstractListModel):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self._items = list(items or [])

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.isValid():
            return self._items[index.row()]
        return None

    # Enable drag + drop
    def flags(self, index):
        default = super().flags(index)
        if index.isValid():
            return default | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return default | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return ["application/x-row"]

    def mimeData(self, indexes):
        mime = QMimeData()
        if indexes:
            mime.setData("application/x-row", str(indexes[0].row()).encode())
        return mime

    def dropMimeData(self, mime, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return False
        if not mime.hasFormat("application/x-row"):
            return False

        src_row = int(bytes(mime.data("application/x-row")).decode())

        # Reject overlapping drops (cursor on top of an item)
        if parent.isValid():
            return False

        # Drop below last row
        if row == -1:
            row = self.rowCount()

        return self.moveRows(QModelIndex(), src_row, 1, QModelIndex(), row)

    def moveRows(self, src_parent, src_row, count, dst_parent, dst_row):
        if count != 1:
            return False
        if src_row == dst_row or src_row + 1 == dst_row:
            return False

        self.beginMoveRows(src_parent, src_row, src_row, dst_parent, dst_row)

        item = self._items.pop(src_row)
        if dst_row > src_row:
            dst_row -= 1
        self._items.insert(dst_row, item)

        self.endMoveRows()
        return True


# ============================================================
#  DELEGATE — Draws a "View" button + hover highlight
# ============================================================
class ButtonDelegate(QStyledItemDelegate):
    clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pressed_index = None

    def paint(self, painter, option, index):
        painter.save()

        # --- Hover highlight ---
        if option.state & QStyle.State_MouseOver:
            hover_color = option.palette.highlight().color().lighter(180)
            painter.fillRect(option.rect, hover_color)

        # Draw background (selection, etc.)
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)

        # Draw text
        text_rect = option.rect.adjusted(8, 0, -80, 0)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, index.data())

        # Draw button
        button_rect = self.buttonRect(option)
        btn = QStyleOptionButton()
        btn.rect = button_rect
        btn.text = "View"
        btn.state = QStyle.State_Enabled

        # Hover state for button
        if option.state & QStyle.State_MouseOver:
            btn.state |= QStyle.State_MouseOver

        # Pressed state
        if self._pressed_index == index:
            btn.state |= QStyle.State_Sunken

        QApplication.style().drawControl(QStyle.CE_PushButton, btn, painter)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if not isinstance(event, QMouseEvent):
            return False

        pos = event.position().toPoint()

        # Press
        if event.type() == QEvent.MouseButtonPress:
            if self.buttonRect(option).contains(pos):
                self._pressed_index = index
                return True

        # Release
        if event.type() == QEvent.MouseButtonRelease:
            if self._pressed_index == index:
                self._pressed_index = None
                if self.buttonRect(option).contains(pos):
                    self.clicked.emit(index.row())
                    return True

        # Move outside button while pressed → cancel press state
        if event.type() == QEvent.MouseMove:
            if self._pressed_index == index:
                if not self.buttonRect(option).contains(pos):
                    self._pressed_index = None

        return False

    def buttonRect(self, option):
        margin = 6
        w = 60
        h = option.rect.height() - margin * 2
        x = option.rect.right() - w - margin
        y = option.rect.top() + margin
        return QRect(x, y, w, h)

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 36)


# ============================================================
#  MAIN WINDOW
# ============================================================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QListView — Reorderable + Button + Hover Highlight")

        items = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
        self.model = ReorderableListModel(items)

        self.view = QListView()
        self.view.setModel(self.model)

        # Enable drag & drop reordering
        self.view.setDragEnabled(True)
        self.view.setAcceptDrops(True)
        self.view.setDropIndicatorShown(True)
        self.view.setDragDropMode(QListView.InternalMove)
        self.view.setDefaultDropAction(Qt.MoveAction)

        # Enable hover events
        self.view.setMouseTracking(True)

        # Delegate
        self.delegate = ButtonDelegate()
        self.view.setItemDelegate(self.delegate)
        self.delegate.clicked.connect(self.on_button_clicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)

    def on_button_clicked(self, row):
        print(f"Button clicked on row {row}: {self.model._items[row]}")


# ============================================================
#  ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.resize(400, 300)
    w.show()
    app.exec()

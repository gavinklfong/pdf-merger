import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QFrame,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPixmap


class DraggableRow(QLabel):
    def __init__(self, text):
        super().__init__(text)

        self.setFixedHeight(40)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("background-color: lightblue; padding-left: 8px;")

        self.opacity = QGraphicsOpacityEffect(self)
        self.opacity.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.text())
        drag.setMimeData(mime)

        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())

        self.opacity.setOpacity(0.4)
        drag.exec(Qt.DropAction.MoveAction)
        self.opacity.setOpacity(1.0)


class TableWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Shape.StyledPanel)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(4)
        self.layout.addStretch()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        source = event.source()
        if not isinstance(source, DraggableRow):
            return

        pos_y = event.position().toPoint().y()
        insert_index = self.layout.count() - 1  # default: before stretch

        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()

            if widget is None or widget is source:
                continue

            if pos_y < widget.y() + widget.height() / 2:
                insert_index = i
                break

        self.layout.insertWidget(insert_index, source)
        event.acceptProposedAction()



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reorderable Table (One Row per Box)")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        table = TableWidget()
        layout.addWidget(table)

        # Initial rows
        for text in ["Row A", "Row B", "Row C", "Row D"]:
            table.layout.insertWidget(
                table.layout.count() - 1,
                DraggableRow(text)
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

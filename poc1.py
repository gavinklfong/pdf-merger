import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPixmap


class DraggableBox(QLabel):
    def __init__(self, text):
        super().__init__(text)

        self.setFrameStyle(QFrame.Shape.Box)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(100, 40)
        self.setStyleSheet("background-color: lightblue;")

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.text())
        drag.setMimeData(mime)

        # 🔹 Create drag pixmap (visual clone)
        pixmap = QPixmap(self.size())
        self.render(pixmap)

        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())

        # 🔹 Dim original widget
        self.opacity_effect.setOpacity(0.4)

        drag.exec(Qt.DropAction.MoveAction)

        # 🔹 Restore after drag
        self.opacity_effect.setOpacity(1.0)


class DropContainer(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(title))
        layout.addStretch()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        source = event.source()
        if isinstance(source, DraggableBox):
            source.setParent(self)
            self.layout().insertWidget(self.layout().count() - 1, source)
            event.acceptProposedAction()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag Preview Follows Mouse")
        self.resize(500, 300)

        layout = QHBoxLayout(self)

        left = DropContainer("Left Panel")
        right = DropContainer("Right Panel")

        left.layout().insertWidget(1, DraggableBox("Box A"))
        left.layout().insertWidget(2, DraggableBox("Box B"))
        right.layout().insertWidget(1, DraggableBox("Box C"))

        layout.addWidget(left)
        layout.addWidget(right)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

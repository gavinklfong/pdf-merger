import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout
)
from file_item_list_widget import FileItemListWidget

# ---------------------------------------------------------
#  Main Window
# ---------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.list = FileItemListWidget()
        self.list.viewFile = self.view_file  # Override viewFile method

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
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem

app = QApplication([])

table = QTableWidget(5, 2)
table.setHorizontalHeaderLabels(["Name", "Value"])

for r in range(5):
    table.setItem(r, 0, QTableWidgetItem(f"Item {r}"))
    table.setItem(r, 1, QTableWidgetItem(str(r)))

# Enable drag-drop row move
table.setDragDropMode(QTableWidget.InternalMove)
table.setSelectionBehavior(QTableWidget.SelectRows)
table.setDragEnabled(True)
table.setAcceptDrops(True)
table.setDropIndicatorShown(True)

table.show()
app.exec()

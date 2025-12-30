from PyQt6.QtWidgets import QTableView
from PyQt6.QtCore import Qt


class FileTableView(QTableView):
    """
    Custom table view for the file list.

    - Handles drag & drop reordering via the model's move_row()
    - Visual drag indicator shown
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        # We manage reordering ourselves; no built-in InternalMove
        self.setDragDropMode(QTableView.DragDropMode.DragDrop)

        # Selection behavior (rows)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

    def dragEnterEvent(self, event):
        if event.mimeData():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        pos = event.position().toPoint()
        target_index = self.indexAt(pos)
        target_row = target_index.row()

        selected_indexes = self.selectedIndexes()
        if not selected_indexes:
            event.ignore()
            return

        source_row = selected_indexes[0].row()

        model = self.model()
        if model is None or target_row < 0 or source_row < 0:
            event.ignore()
            return

        if target_row != source_row:
            model.move_row(source_row, target_row)

        event.acceptProposedAction()

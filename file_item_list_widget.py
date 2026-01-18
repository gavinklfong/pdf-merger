import os
import logging
from PySide6.QtWidgets import ( QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt
from file_item_widget import FileItemWidget
from file_utils import sort_files_by_date

# ---------------------------------------------------------
#  Custom QListWidget with:
#   - internal reordering
#   - external file drop
#   - auto-scroll
#   - drop indicator
#   - hover highlight
# ---------------------------------------------------------
class FileItemListWidget(QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Track sort direction
        self._sortAscending = False

        # Internal drag reorder
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.InternalMove)

        # Auto-scroll
        self.setAutoScroll(True)
        self.setAutoScrollMargin(30)

        # Drop indicator
        self.setDropIndicatorShown(True)

    def addFileItem(self, path):
        
        widget = FileItemWidget(path)

        # IMPORTANT:
        # - item text must contain filename (for drag pixmap)
        # - foreground transparent prevents overlap
        item = QListWidgetItem(os.path.basename(path))
        item.setForeground(Qt.transparent)
        item.setSizeHint(widget.sizeHint())

        self.addItem(item)
        self.setItemWidget(item, widget)

        widget.viewRequested.connect(lambda w=widget: self.viewFileItem(w)) 
        widget.deleteRequested.connect(lambda w=widget: self.removeFileItem(w))

        self._adjustWidthToContents()

    def removeFileItem(self, widget):
        row = self._rowOfWidget(widget)
        logging.debug("Delete:", widget.filePath)

        item = self.item(row)
        if item:
            self.takeItem(row)            

        widget.deleteLater()

    def viewFileItem(self, widget):
        self.viewFile(widget.filePath)

    def viewFile(self, filename):
        logging.debug("View:", filename)

    def getAllFilePaths(self):
        paths = []
        for i in range(self.count()):
            widget = self.itemWidget(self.item(i))
            paths.append(widget.filePath)
        return paths
    
    def removeAllFileItems(self):
        while self.count() > 0:
            item = self.item(0)
            widget = self.itemWidget(item)
            if widget:
                widget.deleteLater()
            self.takeItem(0)

    def sortFilesByDate(self):
        self._sortAscending = not self._sortAscending

        file_paths = self.getAllFilePaths()
        sorted_paths = sort_files_by_date(file_paths, ascending=self._sortAscending)

        self.setUpdatesEnabled(False)
        try:
            self.removeAllFileItems()
            for path in sorted_paths:
                self.addFileItem(path)
        finally:
            self.setUpdatesEnabled(True)

    def _adjustWidthToContents(self):
        max_width = 0
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget:
                max_width = max(max_width, widget.sizeHint().width())

        # Add some padding for margins and scrollbars
        max_width += 40

        # Resize the list widget
        self.setMinimumWidth(max_width)


    def _rowOfWidget(self, widget):
        for i in range(self.count()):
            if self.itemWidget(self.item(i)) is widget:
                return i
        return -1
    

    # -----------------------------------------------------
    #  External file drop support
    # -----------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path:
                    self.handleDroppedFile(path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    # This will be overridden by MainWindow
    def handleDroppedFile(self, path):
        logging.debug("Dropped:", path)
        self.addFileItem(path)
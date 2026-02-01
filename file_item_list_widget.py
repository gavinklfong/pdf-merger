import os
import logging
from PySide6.QtWidgets import ( QListWidget, QListWidgetItem, QLabel)
from PySide6.QtCore import (Qt, Signal)
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

    itemsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Internal drag reorder
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.InternalMove)

        # Auto-scroll
        self.setAutoScroll(True)
        self.setAutoScrollMargin(30)

        # Drop indicator
        self.setDropIndicatorShown(True)

        # --- Empty state label ---
        self.emptyLabel = QLabel("Drag PDF / image files here", self)
        self.emptyLabel.setAlignment(Qt.AlignCenter)
        self.emptyLabel.setStyleSheet("""
                                        color: #888;
                                        font-size: 20px;
                                        font-style: italic;
                                    """)
        self.emptyLabel.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Connect item change signal
        self.itemsChanged.connect(self._updateEmptyLabel)
        self.itemsChanged.connect(self._adjustWidthToContents)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.emptyLabel:
            self.emptyLabel.resize(self.size())

    def addFileItem(self, path):
        
        widget = FileItemWidget(path)

        item = QListWidgetItem()
        # item.setForeground(Qt.transparent)
        item.setSizeHint(widget.sizeHint())

        self.addItem(item)
        self.setItemWidget(item, widget)

        widget.viewRequested.connect(lambda w=widget: self.viewFileItem(w)) 
        widget.deleteRequested.connect(lambda w=widget: self.removeFileItem(w))

        self.itemsChanged.emit()

    def removeFileItem(self, widget):
        row = self._rowOfWidget(widget)
        logging.debug("Delete:", widget.filePath)

        item = self.item(row)
        if item:
            self.takeItem(row)            

        widget.deleteLater()

        self.itemsChanged.emit()

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

        self.itemsChanged.emit()

    def sortFilesByDate(self, ascending):
        file_paths = self.getAllFilePaths()
        sorted_paths = sort_files_by_date(file_paths, ascending=ascending)

        self.removeAllFileItems()
        for path in sorted_paths:
            self.addFileItem(path)
        

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
    
    def _updateEmptyLabel(self):
        self.emptyLabel.setVisible(self.count() == 0)


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
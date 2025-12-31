from PyQt6.QtCore import (
    QAbstractTableModel,
    Qt,
    QModelIndex,
)


class FileListModel(QAbstractTableModel):
    """
    Table model storing a list of files.

    Column 0: Sequence number (#)
    Column 1: File name
    Column 2: Actions (buttons in view; model provides only header/placeholder)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files = []  # list of dicts: { "name": str, "path": str }

    # ---------------------------------------------------------
    # Required Qt model methods
    # ---------------------------------------------------------
    def rowCount(self, parent=QModelIndex()):
        return len(self._files)

    def columnCount(self, parent=QModelIndex()):
        return 3  # #, File, Actions

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        file = self._files[row]

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                # Sequence number (1-based)
                return str(row + 1)
            if col == 1:
                return file["name"]
            if col == 2:
                return ""  # Action column uses widgets

        if role == Qt.ItemDataRole.UserRole:
            return file["path"]

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return ["#", "File", "Actions"][section]

        return None

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def add_file(self, path):
        """Add a file to the model."""
        import os
        name = os.path.basename(path)

        self.beginInsertRows(QModelIndex(), len(self._files), len(self._files))
        self._files.append({"name": name, "path": path})
        self.endInsertRows()

    def remove_row(self, row):
        """Remove a row from the model."""
        if 0 <= row < len(self._files):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._files[row]
            self.endRemoveRows()

    def clear(self):
        """Remove all rows."""
        self.beginResetModel()
        self._files.clear()
        self.endResetModel()

    def move_row(self, source_row, target_row):
        """Move a row from source_row to target_row."""
        if source_row == target_row:
            return
        if not (0 <= source_row < len(self._files)):
            return
        if not (0 <= target_row < len(self._files)):
            return

        # Qt moveRows API requires special destination index
        if target_row > source_row:
            dest = target_row + 1
        else:
            dest = target_row

        self.beginMoveRows(QModelIndex(), source_row, source_row, QModelIndex(), dest)
        item = self._files.pop(source_row)
        self._files.insert(target_row, item)
        self.endMoveRows()

    def move_up(self, row):
        if row > 0:
            self.move_row(row, row - 1)

    def move_down(self, row):
        if row < len(self._files) - 1:
            self.move_row(row, row + 1)

    def get_path(self, row):
        """Return the full path for the given row."""
        if 0 <= row < len(self._files):
            return self._files[row]["path"]
        return None

    def get_paths_in_order(self):
        """Return a list of file paths in the current order."""
        return [f["path"] for f in self._files]

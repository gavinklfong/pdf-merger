from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QFileDialog, QDialog, QMenuBar
)
from PySide6.QtGui import QGuiApplication, QAction
import sys, os, subprocess, logging

from pdf_utils import merge_and_optimize
from merge_pdf_dialog import MergePDFDialog
from file_item_list_widget import FileItemListWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Merger")

        # ---------------------------------------------------------
        # Central widget + layout
        # ---------------------------------------------------------
        central = QWidget(self)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        # ---------------------------------------------------------
        # Menu bar (QMainWindow already has one)
        # ---------------------------------------------------------
        menuBar = self.menuBar()
        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.showAboutDialog)
        menuBar.addAction(aboutAction)

        # ---------------------------------------------------------
        # File item list
        # ---------------------------------------------------------
        self.sortAscending = False
        self.list = FileItemListWidget()
        self.list.viewFile = self.viewFile
        self.list.itemsChanged.connect(self.updateStatusCount)
        layout.addWidget(self.list)

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------
        mergeFileButton = QPushButton("Merge Files")
        mergeFileButton.clicked.connect(self.mergeFileItems)
        mergeFileButton.setStyleSheet("""
            QPushButton {
                background-color: #3e8e41;
                color: white;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3e8e41; }
        """)

        sortFileButton = QPushButton("Sort Files by Date")
        sortFileButton.clicked.connect(self.toggleSort)
        sortFileButton.setStyleSheet("""
            QPushButton {
                background-color: #bdc3c7;
                color: #2c3e50;
            }
            QPushButton:hover { background-color: #aeb6bf; }
            QPushButton:pressed { background-color: #95a5a6; }
        """)

        clearButton = QPushButton("Clear All Items")
        clearButton.clicked.connect(self.list.removeAllFileItems)
        clearButton.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:pressed { background-color: #a93226; }
        """)

        quitButton = QPushButton("Quit")
        quitButton.clicked.connect(self.close)
        quitButton.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
            }
            QPushButton:hover { background-color: #707b7c; }
            QPushButton:pressed { background-color: #616a6b; }
        """)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(sortFileButton)
        buttonLayout.addWidget(mergeFileButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(clearButton)
        buttonLayout.addWidget(quitButton)

        layout.addLayout(buttonLayout)

        # ---------------------------------------------------------
        # Status bar
        # ---------------------------------------------------------
        self.status = self.statusBar()
        self.status.showMessage("0 items")


    # ---------------------------------------------------------
    # Center window
    # ---------------------------------------------------------
    def centerOnScreen(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        size = self.frameGeometry()
        size.moveCenter(screen.center())
        self.move(size.topLeft())

    # ---------------------------------------------------------
    # Update status count
    # ---------------------------------------------------------
    def updateStatusCount(self):
        count = len(self.list.getAllFilePaths())
        self.status.showMessage(f"{count} item(s)")

    # ---------------------------------------------------------
    # About dialog
    # ---------------------------------------------------------
    def showAboutDialog(self):
        QMessageBox.information(
            self,
            "About PDF Merger",
            (
                "PDF Merger\n\n"
                "A simple tool to merge and compress PDF files.\n\n"
                "This application uses PySide6 (Qt for Python),\n"
                "licensed under the LGPL v3.\n\n"
                "Full source code available at:\n"
                "https://github.com/gavinklfong/pdf-merger\n"
            ),
            QMessageBox.Close
        )

    # ---------------------------------------------------------
    # External viewer
    # ---------------------------------------------------------
    def viewFile(self, path):
        try:
            if sys.platform.startswith("darwin"):
                subprocess.run(["open", path])
            elif os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.run(["xdg-open", path])
        except Exception as e:
            QMessageBox.critical(self, "Open Error", str(e))

    # ---------------------------------------------------------
    # Sorting
    # ---------------------------------------------------------
    def toggleSort(self):
        self.sortAscending = not self.sortAscending
        self.list.sortFilesByDate(self.sortAscending)

    # ---------------------------------------------------------
    # Merge files
    # ---------------------------------------------------------
    def mergeFileItems(self):
        file_paths = self.list.getAllFilePaths()

        if not file_paths:
            QMessageBox.warning(self, "No Files", "No files added.")
            return

        dlg = MergePDFDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        settings = dlg.getValues()
        compression = settings["compression"]
        jpeg_quality = settings["jpeg_quality"]

        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF",
            "merged.pdf",
            "PDF Files (*.pdf)"
        )
        if not output_file:
            return

        merge_and_optimize(
            file_paths,
            output_file,
            compression_level=compression,
            jpeg_quality=jpeg_quality
        )

        self.viewFile(output_file)

# ---------------------------------------------------------
#  Run App
# ---------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.centerOnScreen()
    w.resize(800, 400)
    w.show()
    app.exec()
import sys
import os
import subprocess
import logging
from pdf_utils import merge_and_optimize
from merge_pdf_dialog import MergePDFDialog
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QFileDialog, QDialog
)
from file_item_list_widget import FileItemListWidget


logging.basicConfig( 
    level=logging.INFO, 
    format="[%(levelname)s] %(message)s" )

# ---------------------------------------------------------
#  Main Window
# ---------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.sortAscending = False

        self.setWindowTitle("PDF Merger")
        self.list = FileItemListWidget()
        self.list.viewFile = self.viewFile  # Override viewFile method

        layout = QVBoxLayout(self)
        layout.addWidget(self.list)

        mergeFileButton = QPushButton("Merge Files")
        mergeFileButton.clicked.connect(self.mergeFileItems)
        mergeFileButton.setStyleSheet("""
            QPushButton {
                background-color: #3e8e41;      /* modern green */
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;      /* slightly darker on hover */
            }
            QPushButton:pressed {
                background-color: #3e8e41;      /* deeper green when pressed */
            }
        """)


        sortFileButton = QPushButton("Sort Files by Date")
        sortFileButton.clicked.connect(self.toggleSort)
        sortFileButton.setStyleSheet("""
            QPushButton {
                background-color: #bdc3c7;      /* soft grey */
                color: #2c3e50;                 /* dark text for contrast */
            }
            QPushButton:hover {
                background-color: #aeb6bf;      /* slightly darker on hover */
            }
            QPushButton:pressed {
                background-color: #95a5a6;      /* deeper grey when pressed */
            }
        """)


        clearButton = QPushButton("Clear All Items")
        clearButton.clicked.connect(self.list.removeAllFileItems)
        clearButton.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;      /* strong red */
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;      /* darker red on hover */
            }
            QPushButton:pressed {
                background-color: #a93226;      /* deeper red when pressed */
            }
        """)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(sortFileButton)
        buttonLayout.addWidget(mergeFileButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(clearButton)

        layout.addLayout(buttonLayout)


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
    # Sort files
    # ---------------------------------------------------------
    def toggleSort(self):
        self.sortAscending = not self.sortAscending
        self.list.sortFilesByDate(self.sortAscending)

    # ---------------------------------------------------------
    # Merge files
    # ---------------------------------------------------------
    def mergeFileItems(self):

        # --- Retrieve and check input file list ---
        file_paths = self.list.getAllFilePaths()
        
        if not file_paths:
            QMessageBox.warning(self, "No Files", "No files added.")
            return

        # --- Ask for compression settings ---
        dlg = MergePDFDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        settings = dlg.getValues()
        compression = settings["compression"]
        jpeg_quality = settings["jpeg_quality"]

        # --- Ask for output file ---
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF",
            "merged.pdf",
            "PDF Files (*.pdf)"
        )
        if not output_file:
            return

        # Pass settings to your merge function
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
    w.resize(500, 300)
    w.show()
    app.exec()

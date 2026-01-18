import sys
import os
import subprocess
import tempfile
import logging
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QFileDialog
)
from file_item_list_widget import FileItemListWidget
from pdf_merger import merge_files, optimize_pdf_with_ghostscript


logging.basicConfig( 
    level=logging.INFO, 
    format="[%(levelname)s] %(message)s" )

# ---------------------------------------------------------
#  Main Window
# ---------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Merger")
        self.list = FileItemListWidget()
        self.list.viewFile = self.viewFile  # Override viewFile method

        layout = QVBoxLayout(self)
        layout.addWidget(self.list)

        mergeFileButton = QPushButton("Merge Files")
        mergeFileButton.clicked.connect(self.mergeFileItems)

        sortFileButton = QPushButton("Sort Files by Date")
        sortFileButton.clicked.connect(self.list.sortFilesByDate)

        clearButton = QPushButton("Clear All Items")
        clearButton.clicked.connect(self.list.removeAllFileItems)

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
    # Merge files
    # ---------------------------------------------------------
    def mergeFileItems(self):
        file_paths = self.list.getAllFilePaths()
        
        if not file_paths:
            QMessageBox.warning(self, "No Files", "No files added.")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF",
            "merged.pdf",
            "PDF Files (*.pdf)"
        )
        if not output_file:
            return

        # Create a temporary PDF file for output
        fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        try:
            logging.info("Generating merged pdf")
            # Merge files
            merge_files(file_paths, temp_pdf)
            
            # Optimize the merged PDF
            logging.info("Optimizing output pdf")
            optimize_pdf_with_ghostscript(temp_pdf, output_file)

            # Open the resulting file
            self.viewFile(output_file)

        finally:
            # Cleanup temporary files
            try:
                os.remove(temp_pdf)
            except:
                pass

# ---------------------------------------------------------
#  Run App
# ---------------------------------------------------------
app = QApplication(sys.argv)
w = MainWindow()
w.resize(500, 300)
w.show()
app.exec()
import sys, os, subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QFileDialog, QDialog, QProgressBar
)
from PySide6.QtGui import QGuiApplication, QAction
from PySide6.QtCore import QThread, Slot, Qt

from pdf_utils import count_total_pages
from file_item_list_widget import FileItemListWidget
from pdf_merge_dialog import PDFMergeDialog
from pdf_merge_worker import PDFMergeWorker


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
        self.list.itemsChanged.connect(self.updateStatusCount)
        self.list.viewRequested.connect(lambda filePath: self.viewFile(filePath))
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

        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0) 
        self.progressBar.setVisible(False)

        self.statusBar().addPermanentWidget(self.progressBar)


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
    # Merge progress handlers
    # ---------------------------------------------------------
    @Slot(dict)
    def onMergeProgress(self, event):
        msg = event.get("message", "")
        pages = event.get("pages_done")

        # Update status bar text
        self.statusBar().showMessage(msg)

        # Update progress bar
        if pages is not None:
            # Switch from busy mode to determinate mode on first page update
            if self.progressBar.maximum() == 0:
                # You can compute total pages if you want, but if not:
                # just show a growing bar with no max
                self.progressBar.setMaximum(0)  # stays busy
            else:
                self.progressBar.setValue(pages)

    @Slot()
    def onMergeFinished(self):

        # Restore normal cursor 
        QApplication.restoreOverrideCursor()

        # Hide progress bar
        self.progressBar.setVisible(False)
        self.progressBar.setValue(0)

        # Get output file size
        output_file = getattr(self, "_current_output_file", "")

        if output_file:
            size_bytes = Path(output_file).stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = "0 bytes"

        self.statusBar().showMessage(
            f"Merge completed successfully: {output_file} ({size_str})"
        )

        # Open the merged PDF
        if hasattr(self, "_current_output_file"):
            self.viewFile(self._current_output_file)


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

        # Get file paths
        file_paths = self.list.getAllFilePaths()
        if not file_paths:
            QMessageBox.warning(self, "No Files", "No files added.")
            return

        # Get compression settings
        pdf_merge_dialog = PDFMergeDialog(self)
        if pdf_merge_dialog.exec() != QDialog.Accepted:
            return

        settings = pdf_merge_dialog.getValues()
        compression = settings["compression"]
        jpeg_quality = settings["jpeg_quality"]

        # Get output file path
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF",
            "merged.pdf",
            "PDF Files (*.pdf)"
        )
        if not output_file:
            return

        # Show busy cursor 
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Keep reference to output file for later viewing
        self._current_output_file = output_file

        # Setup progress bar
        total_pages = count_total_pages(file_paths)
        self.progressBar.setVisible(True) 
        self.progressBar.setMinimum(0) 
        self.progressBar.setMaximum(total_pages)
        self.progressBar.setValue(0)

        # Start worker thread
        self.worker = PDFMergeWorker(
            file_paths,
            output_file,
            jpeg_quality,
            compression
        )

        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.progress.connect(self.onMergeProgress)
        self.worker.finished.connect(self.onMergeFinished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)


        self.thread.start()
        self.statusBar().showMessage("Starting merge…")


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



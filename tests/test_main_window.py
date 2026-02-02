import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal, QObject
from main import MainWindow
from pypdf import PdfWriter
import sys
import os


def make_pdf(path):
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(path, "wb") as f:
        writer.write(f)


def test_window_initializes(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    assert win.windowTitle() == "PDF Merger"
    assert win.list.count() == 0
    assert win.sortAscending is False


def test_toggle_sort_calls_list_sort(qtbot, tmp_path):
    win = MainWindow()
    qtbot.addWidget(win)

    # Add two files
    f1 = tmp_path / "file_2020_01.pdf"
    f2 = tmp_path / "file_2021_02.pdf"
    make_pdf(f1)
    make_pdf(f2)

    win.list.addFileItem(str(f1))
    win.list.addFileItem(str(f2))

    with patch.object(win.list, "sortFilesByDate") as mock_sort:
        win.toggleSort()
        mock_sort.assert_called_once_with(True)

        win.toggleSort()
        mock_sort.assert_called_with(False)


def test_merge_no_files_shows_warning(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    with patch("main.QMessageBox.warning") as mock_warning:
        win.mergeFileItems()
        mock_warning.assert_called_once()

def test_merge_with_files_calls_merge_and_optimize(qtbot, tmp_path):
    win = MainWindow()
    qtbot.addWidget(win)

    # Create fake input files
    f1 = tmp_path / "a.pdf"
    f2 = tmp_path / "b.pdf"
    make_pdf(f1)
    make_pdf(f2)

    win.list.addFileItem(str(f1))
    win.list.addFileItem(str(f2))

    # Mock dialog
    mock_dialog = MagicMock()
    mock_dialog.exec.return_value = QDialog.Accepted
    mock_dialog.getValues.return_value = {
        "compression": "Medium",
        "jpeg_quality": 80,
    }

    # --- Fake worker to avoid real threading ---
    class FakeWorker(QObject):
        progress = Signal(dict)
        finished = Signal()

        def __init__(self, *args, **kwargs):
            super().__init__()

        def run(self):
            # Simulate merge finishing instantly
            self.progress.emit({"message": "done"})
            self.finished.emit()

    with patch("main.count_total_pages", return_value=2), \
        patch("main.Path") as MockPath, \
        patch("main.PDFMergeDialog", return_value=mock_dialog), \
        patch("main.QFileDialog.getSaveFileName", return_value=("output.pdf", None)), \
        patch("main.PDFMergeWorker", FakeWorker), \
        patch.object(win, "viewFile") as mock_view:

        MockPath.return_value.stat.return_value.st_size = 1234

        win.mergeFileItems()

        # Allow Qt event loop to process signals
        qtbot.waitUntil(lambda: mock_view.called, timeout=1000)

        mock_dialog.exec.assert_called_once()
        mock_dialog.getValues.assert_called_once()
        mock_view.assert_called_once_with("output.pdf")

def test_view_file_calls_correct_os_command(qtbot, tmp_path):
    win = MainWindow()
    qtbot.addWidget(win)

    fake_file = str(tmp_path / "test.pdf")

    if sys.platform.startswith("darwin"):
        with patch("subprocess.run") as mock_run:
            win.viewFile(fake_file)
            mock_run.assert_called_once()
    elif os.name == "nt":
        with patch("os.startfile") as mock_start:
            win.viewFile(fake_file)
            mock_start.assert_called_once()
    elif os.name == "posix":
        with patch("subprocess.run") as mock_run:
            win.viewFile(fake_file)
            mock_run.assert_called_once()

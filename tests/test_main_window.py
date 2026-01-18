import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QPushButton
from main import MainWindow
import sys
import os

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
    f1.write_text("x")
    f2.write_text("y")

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

    # Add fake files
    f1 = tmp_path / "a.pdf"
    f2 = tmp_path / "b.pdf"
    f1.write_text("x")
    f2.write_text("y")

    win.list.addFileItem(str(f1))
    win.list.addFileItem(str(f2))

    # Mock file dialog
    with patch("main.QFileDialog.getSaveFileName", return_value=("output.pdf", None)):
        # Mock merge + optimize
        with patch("main.merge_files") as mock_merge, \
             patch("main.optimize_pdf_with_ghostscript") as mock_opt, \
             patch.object(win, "viewFile") as mock_view:

            win.mergeFileItems()

            assert mock_merge.called
            assert mock_opt.called
            assert mock_view.called


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

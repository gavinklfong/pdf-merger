import pytest
from PyQt6.QtWidgets import QWidget, QPushButton, QMenuBar

from main import PDFMergerApp
from views.file_table_view import FileTableView
from models.file_list_model import FileListModel


def test_main_window_initializes(qtbot):
    """Ensure the main window loads without errors and UI elements exist."""

    window = PDFMergerApp()
    qtbot.addWidget(window)

    # Window should be a QWidget
    assert isinstance(window, QWidget)

    # Table should be replaced with FileTableView
    assert isinstance(window.table, FileTableView)

    # Model should be attached
    assert isinstance(window.model, FileListModel)
    assert window.table.model() is window.model

    # Buttons should exist
    assert isinstance(window.add_btn, QPushButton)
    assert isinstance(window.merge_btn, QPushButton)
    assert isinstance(window.remove_all_btn, QPushButton)

    # Menu bar should exist
    menubar = window.findChild(QMenuBar)
    assert menubar is not None

    # Preferences action should exist
    assert hasattr(window, "actionPreferences")

    # Show window (integration-level test)
    window.show()
    assert window.isVisible()


import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QMenuBar

from main import PDFMergerApp
from views.file_table_view import FileTableView
from models.file_list_model import FileListModel


def test_main_window_initializes(qtbot):
    """Ensure the main window loads without errors and UI elements exist."""

    window = PDFMergerApp()
    qtbot.addWidget(window)

    assert isinstance(window, QWidget)
    assert isinstance(window.table, FileTableView)
    assert isinstance(window.model, FileListModel)
    assert window.table.model() is window.model

    assert isinstance(window.add_btn, QPushButton)
    assert isinstance(window.merge_btn, QPushButton)
    assert isinstance(window.remove_all_btn, QPushButton)

    menubar = window.findChild(QMenuBar)
    assert menubar is not None

    assert hasattr(window, "actionPreferences")

    window.show()
    assert window.isVisible()
import pytest
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
from PyQt6.QtCore import Qt

from models.file_list_model import FileListModel
from views.file_table_view import FileTableView


# ---------------------------------------------------------
# Fake actions controller for testing signal connections
# ---------------------------------------------------------
class FakeActions:
    def __init__(self):
        self.up_called = False
        self.down_called = False
        self.view_called = False
        self.remove_called = False

    def on_up_clicked(self):
        self.up_called = True

    def on_down_clicked(self):
        self.down_called = True

    def on_view_clicked(self):
        self.view_called = True

    def on_remove_clicked(self):
        self.remove_called = True


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------
def test_create_action_widget(qtbot):
    # Setup model
    model = FileListModel()
    model.add_file("/tmp/a.pdf")

    # Setup view
    view = FileTableView()
    view.setModel(model)
    qtbot.addWidget(view)

    # Fake actions controller
    actions = FakeActions()

    # Create widget for row 0
    view.create_action_widget(0, actions)

    # Retrieve the widget placed in column 1
    index = model.index(0, 2)
    widget = view.indexWidget(index)

    assert widget is not None
    assert isinstance(widget, QWidget)

    # Extract buttons
    buttons = widget.findChildren(QPushButton)
    labels = sorted([b.text() for b in buttons])

    assert labels == ["Down", "Remove", "Up", "View"]

    # Click each button and verify callback
    for btn in buttons:
        if btn.text() == "Up":
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
            assert actions.up_called

        if btn.text() == "Down":
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
            assert actions.down_called

        if btn.text() == "View":
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
            assert actions.view_called

        if btn.text() == "Remove":
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
            assert actions.remove_called


def test_action_widget_replaces_existing(qtbot):
    model = FileListModel()
    model.add_file("/tmp/a.pdf")

    view = FileTableView()
    view.setModel(model)
    qtbot.addWidget(view)

    actions = FakeActions()

    # First creation
    view.create_action_widget(0, actions)
    index = model.index(0, 2)
    widget1 = view.indexWidget(index)

    # Second creation should replace the widget
    view.create_action_widget(0, actions)
    widget2 = view.indexWidget(index)

    assert widget1 is not widget2

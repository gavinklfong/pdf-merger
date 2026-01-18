import os
import pytest
from PySide6.QtWidgets import QPushButton
from file_item_widget import FileItemWidget   # adjust import to your project

def test_file_item_widget_basic_properties(qtbot, tmp_path):
    # Arrange
    fake_file = tmp_path / "example.txt"
    fake_file.write_text("dummy")  # not required, but realistic

    widget = FileItemWidget(str(fake_file))
    qtbot.addWidget(widget)

    # Assert: label text is basename
    assert widget.label.text() == "example.txt"

    # Assert: tooltip is full path
    assert widget.toolTip() == str(fake_file)

    # Assert: mouse tracking enabled
    assert widget.hasMouseTracking() is True


def test_file_item_widget_signals(qtbot, tmp_path):
    # Arrange
    fake_file = tmp_path / "example.txt"
    fake_file.write_text("dummy")

    widget = FileItemWidget(str(fake_file))
    qtbot.addWidget(widget)

    # Find buttons
    buttons = widget.findChildren(QPushButton)
    assert len(buttons) == 2

    btn_view = next(b for b in buttons if b.text() == "View")
    btn_delete = next(b for b in buttons if b.text() == "Delete")

    # Prepare signal spies
    view_spy = qtbot.waitSignal(widget.viewRequested, timeout=100)
    delete_spy = qtbot.waitSignal(widget.deleteRequested, timeout=100)

    # Act: click buttons
    btn_view.click()
    btn_delete.click()

    # Assert: signals emitted
    assert view_spy.signal_triggered
    assert delete_spy.signal_triggered

import os
import pytest
from PySide6.QtWidgets import QPushButton, QStyle
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


def test_file_item_widget_icons(qtbot, tmp_path):
    fake_file = tmp_path / "example.txt"
    fake_file.write_text("dummy")

    widget = FileItemWidget(str(fake_file))
    qtbot.addWidget(widget)

    btn_view = widget.btn_view
    btn_delete = widget.btn_delete

    # --- Verify View icon (SP_FileIcon) ---
    expected_view_icon = widget.style().standardIcon(QStyle.SP_FileIcon)
    expected_view_pixmap = expected_view_icon.pixmap(24, 24)
    actual_view_pixmap = btn_view.icon().pixmap(24, 24)

    assert not expected_view_pixmap.isNull()
    assert not actual_view_pixmap.isNull()
    assert expected_view_pixmap.toImage() == actual_view_pixmap.toImage()

    # --- Verify Delete icon (SP_TrashIcon) ---
    expected_delete_icon = widget.style().standardIcon(QStyle.SP_TrashIcon)
    expected_delete_pixmap = expected_delete_icon.pixmap(24, 24)
    actual_delete_pixmap = btn_delete.icon().pixmap(24, 24)

    assert not expected_delete_pixmap.isNull()
    assert not actual_delete_pixmap.isNull()
    assert expected_delete_pixmap.toImage() == actual_delete_pixmap.toImage()

def test_file_item_widget_signals(qtbot, tmp_path):
    # Arrange
    fake_file = tmp_path / "example.txt"
    fake_file.write_text("dummy")

    widget = FileItemWidget(str(fake_file))
    qtbot.addWidget(widget)

    # Buttons no longer have text, so use attributes
    btn_view = widget.btn_view
    btn_delete = widget.btn_delete

    assert isinstance(btn_view, QPushButton)
    assert isinstance(btn_delete, QPushButton)

    # Prepare signal spies
    view_spy = qtbot.waitSignal(widget.viewRequested, timeout=200)
    delete_spy = qtbot.waitSignal(widget.deleteRequested, timeout=200)

    # Act
    btn_view.click()
    btn_delete.click()

    # Assert
    assert view_spy.signal_triggered
    assert delete_spy.signal_triggered


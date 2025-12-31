import pytest
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest

from models.file_list_model import FileListModel
from views.file_table_view import FileTableView


@pytest.fixture
def setup_view(qtbot):
    """Create a FileTableView + FileListModel pair."""
    model = FileListModel()
    view = FileTableView()
    view.setModel(model)

    qtbot.addWidget(view)
    view.show()

    return model, view


def test_drag_drop_reorder_down(qtbot, setup_view):
    model, view = setup_view

    # Add sample files
    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")
    model.add_file("/tmp/c.pdf")

    assert model.get_paths_in_order() == [
        "/tmp/a.pdf",
        "/tmp/b.pdf",
        "/tmp/c.pdf",
    ]

    # Select row 0 ("a.pdf")
    index_a = model.index(0, 0)
    view.setCurrentIndex(index_a)

    # Simulate drag from row 0 → row 2
    start_pos = view.visualRect(index_a).center()
    target_index = model.index(2, 0)
    end_pos = view.visualRect(target_index).center()

    QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, pos=start_pos)
    QTest.mouseMove(view.viewport(), pos=end_pos)
    QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton, pos=end_pos)

    # Expect "a.pdf" moved to bottom
    assert model.get_paths_in_order() == [
        "/tmp/b.pdf",
        "/tmp/c.pdf",
        "/tmp/a.pdf",
    ]


def test_drag_drop_reorder_up(qtbot, setup_view):
    model, view = setup_view

    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")
    model.add_file("/tmp/c.pdf")

    # Select row 2 ("c.pdf")
    index_c = model.index(2, 0)
    view.setCurrentIndex(index_c)

    # Drag row 2 → row 0
    start_pos = view.visualRect(index_c).center()
    target_index = model.index(0, 0)
    end_pos = view.visualRect(target_index).center()

    QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, pos=start_pos)
    QTest.mouseMove(view.viewport(), pos=end_pos)
    QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton, pos=end_pos)

    assert model.get_paths_in_order() == [
        "/tmp/c.pdf",
        "/tmp/a.pdf",
        "/tmp/b.pdf",
    ]


def test_drag_drop_noop_same_row(qtbot, setup_view):
    model, view = setup_view

    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")

    index_a = model.index(0, 0)
    view.setCurrentIndex(index_a)

    pos = view.visualRect(index_a).center()

    # Drag and drop onto itself
    QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, pos=pos)
    QTest.mouseMove(view.viewport(), pos=pos)
    QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton, pos=pos)

    # Order should remain unchanged
    assert model.get_paths_in_order() == [
        "/tmp/a.pdf",
        "/tmp/b.pdf",
    ]


def test_drag_drop_outside_table(qtbot, setup_view):
    model, view = setup_view

    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")

    index_a = model.index(0, 0)
    view.setCurrentIndex(index_a)

    start_pos = view.visualRect(index_a).center()
    end_pos = QPoint(-50, -50)  # outside table

    QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, pos=start_pos)
    QTest.mouseMove(view.viewport(), pos=end_pos)
    QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton, pos=end_pos)

    # No change expected
    assert model.get_paths_in_order() == [
        "/tmp/a.pdf",
        "/tmp/b.pdf",
    ]

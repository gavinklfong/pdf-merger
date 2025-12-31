import pytest
from models.file_list_model import FileListModel


def test_initial_state():
    model = FileListModel()
    assert model.rowCount() == 0
    assert model.columnCount() == 2


def test_add_file():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")

    assert model.rowCount() == 1
    assert model.get_path(0) == "/tmp/a.pdf"
    assert model.get_paths_in_order() == ["/tmp/a.pdf"]

    # Check display role
    index = model.index(0, 0)
    assert model.data(index) == "a.pdf"


def test_add_multiple_files():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")
    model.add_file("/tmp/c.pdf")

    assert model.rowCount() == 3
    assert model.get_paths_in_order() == [
        "/tmp/a.pdf",
        "/tmp/b.pdf",
        "/tmp/c.pdf",
    ]


def test_remove_row():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")

    model.remove_row(0)

    assert model.rowCount() == 1
    assert model.get_path(0) == "/tmp/b.pdf"


def test_remove_row_out_of_range():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")

    # Should not crash
    model.remove_row(5)

    assert model.rowCount() == 1


def test_clear():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")

    model.clear()

    assert model.rowCount() == 0
    assert model.get_paths_in_order() == []


def test_move_up():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")
    model.add_file("/tmp/c.pdf")

    model.move_up(2)  # move c above b

    assert model.get_paths_in_order() == [
        "/tmp/a.pdf",
        "/tmp/c.pdf",
        "/tmp/b.pdf",
    ]


def test_move_down():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")
    model.add_file("/tmp/c.pdf")

    model.move_down(0)  # move a below b

    assert model.get_paths_in_order() == [
        "/tmp/b.pdf",
        "/tmp/a.pdf",
        "/tmp/c.pdf",
    ]


def test_move_row_to_specific_position():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")
    model.add_file("/tmp/b.pdf")
    model.add_file("/tmp/c.pdf")

    model.move_row(0, 2)  # move a to bottom

    assert model.get_paths_in_order() == [
        "/tmp/b.pdf",
        "/tmp/c.pdf",
        "/tmp/a.pdf",
    ]


def test_get_path_out_of_range():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")

    assert model.get_path(5) is None

import pytest
from PyQt6.QtCore import Qt, QModelIndex

from file_list_model import FileListModel


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def create_model_with_files(paths):
    model = FileListModel()
    for p in paths:
        model.add_file(p)
    return model


# ---------------------------------------------------------
# Basic structure tests
# ---------------------------------------------------------
def test_initial_state():
    model = FileListModel()
    assert model.rowCount() == 0
    assert model.columnCount() == 3


def test_add_file_increases_row_count():
    model = FileListModel()
    model.add_file("/tmp/a.pdf")
    assert model.rowCount() == 1

    model.add_file("/tmp/b.pdf")
    assert model.rowCount() == 2


def test_data_display_role():
    model = create_model_with_files(["/tmp/a.pdf"])

    index_seq = model.index(0, 0)
    index_name = model.index(0, 1)
    index_actions = model.index(0, 2)

    assert model.data(index_seq, Qt.ItemDataRole.DisplayRole) == "1"
    assert model.data(index_name, Qt.ItemDataRole.DisplayRole) == "a.pdf"
    assert model.data(index_actions, Qt.ItemDataRole.DisplayRole) == ""


def test_data_user_role():
    model = create_model_with_files(["/tmp/a.pdf"])
    index = model.index(0, 0)

    assert model.data(index, Qt.ItemDataRole.UserRole) == "/tmp/a.pdf"


def test_header_labels():
    model = FileListModel()
    assert model.headerData(0, Qt.Orientation.Horizontal) == "#"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "File"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Actions"


# ---------------------------------------------------------
# Removal tests
# ---------------------------------------------------------
def test_remove_row():
    model = create_model_with_files(["/tmp/a.pdf", "/tmp/b.pdf"])

    model.remove_row(0)
    assert model.rowCount() == 1
    assert model.get_path(0) == "/tmp/b.pdf"


def test_remove_row_out_of_range():
    model = create_model_with_files(["/tmp/a.pdf"])
    model.remove_row(5)  # should do nothing
    assert model.rowCount() == 1


# ---------------------------------------------------------
# Clear tests
# ---------------------------------------------------------
def test_clear_model():
    model = create_model_with_files(["/tmp/a.pdf", "/tmp/b.pdf"])
    model.clear()
    assert model.rowCount() == 0
    assert model.get_paths_in_order() == []


# ---------------------------------------------------------
# Move tests
# ---------------------------------------------------------
def test_move_row_down():
    model = create_model_with_files(["/tmp/a.pdf", "/tmp/b.pdf", "/tmp/c.pdf"])

    model.move_row(0, 2)
    assert model.get_paths_in_order() == [
        "/tmp/b.pdf",
        "/tmp/c.pdf",
        "/tmp/a.pdf",
    ]


def test_move_row_up():
    model = create_model_with_files(["/tmp/a.pdf", "/tmp/b.pdf", "/tmp/c.pdf"])

    model.move_row(2, 0)
    assert model.get_paths_in_order() == [
        "/tmp/c.pdf",
        "/tmp/a.pdf",
        "/tmp/b.pdf",
    ]


def test_move_row_no_op_same_index():
    model = create_model_with_files(["/tmp/a.pdf", "/tmp/b.pdf"])
    model.move_row(1, 1)
    assert model.get_paths_in_order() == ["/tmp/a.pdf", "/tmp/b.pdf"]


def test_move_row_out_of_range():
    model = create_model_with_files(["/tmp/a.pdf", "/tmp/b.pdf"])
    model.move_row(5, 0)  # invalid
    assert model.get_paths_in_order() == ["/tmp/a.pdf", "/tmp/b.pdf"]


def test_move_up():
    model = create_model_with_files(["/tmp/a.pdf", "/tmp/b.pdf"])
    model.move_up(1)
    assert model.get_paths_in_order() == ["/tmp/b.pdf", "/tmp/a.pdf"]


def test_move_down():
    model = create_model_with_files(["/tmp/a.pdf", "/tmp/b.pdf"])
    model.move_down(0)
    assert model.get_paths_in_order() == ["/tmp/b.pdf", "/tmp/a.pdf"]


# ---------------------------------------------------------
# Path access tests
# ---------------------------------------------------------
def test_get_path_valid():
    model = create_model_with_files(["/tmp/a.pdf"])
    assert model.get_path(0) == "/tmp/a.pdf"


def test_get_path_invalid():
    model = create_model_with_files(["/tmp/a.pdf"])
    assert model.get_path(5) is None


def test_get_paths_in_order():
    model = create_model_with_files(["/tmp/a.pdf", "/tmp/b.pdf"])
    assert model.get_paths_in_order() == ["/tmp/a.pdf", "/tmp/b.pdf"]

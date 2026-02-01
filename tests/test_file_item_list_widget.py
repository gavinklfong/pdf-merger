import pytest
from PySide6.QtWidgets import QListWidgetItem
from file_item_list_widget import FileItemListWidget
from file_item_widget import FileItemWidget


def test_add_file_item(qtbot, tmp_path):
    widget = FileItemListWidget()
    qtbot.addWidget(widget)

    file1 = tmp_path / "A_2021_01.pdf"
    file1.write_text("dummy")

    widget.addFileItem(str(file1))

    assert widget.count() == 1
    item = widget.item(0)
    child = widget.itemWidget(item)

    assert isinstance(child, FileItemWidget)
    assert child.filePath == str(file1)


def test_get_all_file_paths(qtbot, tmp_path):
    widget = FileItemListWidget()
    qtbot.addWidget(widget)

    f1 = tmp_path / "file_2020_01.pdf"
    f2 = tmp_path / "file_2021_02.pdf"
    f1.write_text("x")
    f2.write_text("y")

    widget.addFileItem(str(f1))
    widget.addFileItem(str(f2))

    paths = widget.getAllFilePaths()
    assert paths == [str(f1), str(f2)]


def test_remove_file_item(qtbot, tmp_path):
    widget = FileItemListWidget()
    qtbot.addWidget(widget)

    f1 = tmp_path / "file.pdf"
    f1.write_text("x")

    widget.addFileItem(str(f1))
    item = widget.item(0)
    child = widget.itemWidget(item)

    widget.removeFileItem(child)

    assert widget.count() == 0


def test_remove_all_file_items(qtbot, tmp_path):
    widget = FileItemListWidget()
    qtbot.addWidget(widget)

    for name in ["a.pdf", "b.pdf", "c.pdf"]:
        p = tmp_path / name
        p.write_text("x")
        widget.addFileItem(str(p))

    widget.removeAllFileItems()
    assert widget.count() == 0


def test_sort_files_by_date(qtbot, tmp_path):
    widget = FileItemListWidget()
    qtbot.addWidget(widget)

    f1 = tmp_path / "file_2021_03.pdf"
    f2 = tmp_path / "file_2020_01.pdf"
    f3 = tmp_path / "file_2022_02.pdf"

    for f in (f1, f2, f3):
        f.write_text("x")
        widget.addFileItem(str(f))

    widget.sortFilesByDate(ascending=True)
    paths = widget.getAllFilePaths()

    assert paths == [str(f2), str(f1), str(f3)]  # 2020, 2021, 2022

    widget.sortFilesByDate(ascending=False)
    paths = widget.getAllFilePaths()

    assert paths == [str(f3), str(f1), str(f2)]  # 2022, 2021, 2020


def test_row_of_widget(qtbot, tmp_path):
    widget = FileItemListWidget()
    qtbot.addWidget(widget)

    f1 = tmp_path / "a.pdf"
    f2 = tmp_path / "b.pdf"
    f1.write_text("x")
    f2.write_text("y")

    widget.addFileItem(str(f1))
    widget.addFileItem(str(f2))

    item0 = widget.itemWidget(widget.item(0))
    item1 = widget.itemWidget(widget.item(1))

    assert widget._rowOfWidget(item0) == 0
    assert widget._rowOfWidget(item1) == 1


def test_adjust_width_to_contents(qtbot, tmp_path):
    widget = FileItemListWidget()
    qtbot.addWidget(widget)

    long_name = tmp_path / ("X" * 80 + ".pdf")
    long_name.write_text("x")

    widget.addFileItem(str(long_name))

    assert widget.minimumWidth() > 100  # should expand


def test_handle_dropped_file(qtbot, tmp_path):
    widget = FileItemListWidget()
    qtbot.addWidget(widget)

    f = tmp_path / "drop_test.pdf"
    f.write_text("x")

    widget._handleDroppedFile(str(f))

    assert widget.count() == 1
    assert widget.getAllFilePaths() == [str(f)]

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from merge_pdf_dialog import MergePDFDialog, COMPRESSION_LABELS


def test_dialog_defaults(qtbot):
    dlg = MergePDFDialog()
    qtbot.addWidget(dlg)

    # Default compression slider value
    assert dlg.compSlider.value() == 1
    assert dlg.compLabel.text() == "Medium"

    # Default JPEG quality
    assert dlg.jpegSlider.value() == 80
    assert dlg.jpegLabel.text() == "80"


def test_compression_slider_updates_label(qtbot):
    dlg = MergePDFDialog()
    qtbot.addWidget(dlg)

    # Move slider to "High" (index 2)
    dlg.compSlider.setValue(2)
    assert dlg.compLabel.text() == COMPRESSION_LABELS[2]

    # Move slider to "Lowest" (index 0)
    dlg.compSlider.setValue(0)
    assert dlg.compLabel.text() == COMPRESSION_LABELS[0]


def test_jpeg_slider_updates_label(qtbot):
    dlg = MergePDFDialog()
    qtbot.addWidget(dlg)

    dlg.jpegSlider.setValue(55)
    assert dlg.jpegLabel.text() == "55"

    dlg.jpegSlider.setValue(100)
    assert dlg.jpegLabel.text() == "100"


def test_get_values_returns_correct_data(qtbot):
    dlg = MergePDFDialog()
    qtbot.addWidget(dlg)

    dlg.compSlider.setValue(3)   # Highest
    dlg.jpegSlider.setValue(42)

    values = dlg.getValues()
    assert values["compression"] == "Highest"
    assert values["jpeg_quality"] == 42


def test_ok_button_accepts_dialog(qtbot):
    dlg = MergePDFDialog()
    qtbot.addWidget(dlg)

    qtbot.mouseClick(dlg.okBtn, Qt.LeftButton)
    assert dlg.result() == QDialog.Accepted


def test_cancel_button_rejects_dialog(qtbot):
    dlg = MergePDFDialog()
    qtbot.addWidget(dlg)

    qtbot.mouseClick(dlg.cancelBtn, Qt.LeftButton)
    assert dlg.result() == QDialog.Rejected


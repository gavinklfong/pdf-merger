import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

from logic.pdf_utils import convert_image_to_pdf, merge_files


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def create_temp_image(ext=".jpg", size=(100, 100), color=(255, 0, 0)):
    """Create a temporary image file and return its path."""
    fd, path = tempfile.mkstemp(suffix=ext)
    os.close(fd)

    img = Image.new("RGB", size, color)
    img.save(path)

    return path


def create_temp_pdf():
    """Create a simple 1-page PDF using Pillow."""
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    img = Image.new("RGB", (200, 200), (0, 255, 0))
    img.save(path, "PDF")

    return path


# ---------------------------------------------------------
# convert_image_to_pdf tests
# ---------------------------------------------------------
def test_convert_jpg_to_pdf():
    jpg_path = create_temp_image(".jpg")

    pdf_path, temp_files = convert_image_to_pdf(jpg_path)

    assert os.path.isfile(pdf_path)
    assert pdf_path in temp_files

    # Validate PDF
    reader = PdfReader(pdf_path)
    assert len(reader.pages) == 1

    # Cleanup
    for f in temp_files:
        os.remove(f)


def test_convert_png_to_pdf():
    png_path = create_temp_image(".png")

    pdf_path, temp_files = convert_image_to_pdf(png_path)

    # PNG conversion creates a temp JPG + temp PDF
    assert len(temp_files) == 2
    assert any(f.endswith(".jpg") for f in temp_files)
    assert any(f.endswith(".pdf") for f in temp_files)

    # Validate PDF
    reader = PdfReader(pdf_path)
    assert len(reader.pages) == 1

    # Cleanup
    for f in temp_files:
        os.remove(f)


# ---------------------------------------------------------
# merge_files tests
# ---------------------------------------------------------
def test_merge_pdfs_only():
    pdf1 = create_temp_pdf()
    pdf2 = create_temp_pdf()

    fd, output = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    merge_files([pdf1, pdf2], output)

    assert os.path.isfile(output)

    reader = PdfReader(output)
    assert len(reader.pages) == 2

    os.remove(pdf1)
    os.remove(pdf2)
    os.remove(output)


def test_merge_images_only():
    img1 = create_temp_image(".jpg")
    img2 = create_temp_image(".png")

    fd, output = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    merge_files([img1, img2], output)

    assert os.path.isfile(output)

    reader = PdfReader(output)
    assert len(reader.pages) == 2

    os.remove(img1)
    os.remove(img2)
    os.remove(output)


def test_merge_mixed_files():
    pdf = create_temp_pdf()
    img = create_temp_image(".jpg")

    fd, output = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    merge_files([pdf, img], output)

    assert os.path.isfile(output)

    reader = PdfReader(output)
    assert len(reader.pages) == 2

    os.remove(pdf)
    os.remove(img)
    os.remove(output)


def test_merge_skips_unsupported_files(capfd):
    pdf = create_temp_pdf()

    fd, output = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    merge_files([pdf, "unsupported.xyz"], output)

    captured = capfd.readouterr()
    assert "Skipping unsupported file" in captured.out

    reader = PdfReader(output)
    assert len(reader.pages) == 1

    os.remove(pdf)
    os.remove(output)

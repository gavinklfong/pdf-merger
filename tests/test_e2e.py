import pytest
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw
import easyocr
from pdf2image import convert_from_path
import numpy as np


def create_two_page_pdf(path):
    c = canvas.Canvas(str(path), pagesize=letter)
    c.drawString(100, 750, "This is page 1 of the test PDF.")
    c.showPage()
    c.drawString(100, 750, "This is page 2 of the test PDF.")
    c.showPage()
    c.save()


def create_image_with_graphics(path):
    img = Image.new("RGB", (300, 200), color="white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 280, 180], outline="black", width=3)
    draw.text((40, 90), "Sample Image Text", fill="black")
    img.save(path, format="PNG")


def test_merge_files_real_pdf_and_image(tmp_path):
    pdf_path = tmp_path / "input_pdf_runtime.pdf"
    img_path = tmp_path / "input_image_runtime.png"
    output_pdf = tmp_path / "merged_output_runtime.pdf"

    create_two_page_pdf(pdf_path)
    create_image_with_graphics(img_path)

    import pdf_utils
    pdf_utils.merge_files([str(pdf_path), str(img_path)], str(output_pdf))

    assert output_pdf.exists()

    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) == 3

    assert "page 1" in reader.pages[0].extract_text()
    assert "page 2" in reader.pages[1].extract_text()

    # ---------------------------
    # OCR page 3 using EasyOCR
    # ---------------------------
    # Render page 3 (index 2) to an image
    images = convert_from_path(str(output_pdf), dpi=300, first_page=3, last_page=3)
    assert len(images) == 1

    page3_img = images[0]

    # Run EasyOCR
    ocr = easyocr.Reader(["en"], gpu=False)
    results = ocr.readtext(np.array(page3_img), detail=0)

    normalized = " ".join(" ".join(results).split()).lower()
    assert "sample image text" in normalized, f"OCR output: {results}"

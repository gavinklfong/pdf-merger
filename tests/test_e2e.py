import pytest
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw


def create_two_page_pdf(path):
    """Create a real 2-page PDF with text."""
    c = canvas.Canvas(str(path), pagesize=letter)

    c.drawString(100, 750, "This is page 1 of the test PDF.")
    c.showPage()

    c.drawString(100, 750, "This is page 2 of the test PDF.")
    c.showPage()

    c.save()


def create_image_with_graphics(path):
    """Create a PNG image with graphics and text."""
    img = Image.new("RGB", (300, 200), color="white")
    draw = ImageDraw.Draw(img)

    draw.rectangle([20, 20, 280, 180], outline="black", width=3)
    draw.text((40, 90), "Sample Image Text", fill="black")

    img.save(path, format="PNG")


def test_merge_files_real_pdf_and_image(tmp_path):
    # ----------------------------------------------------
    # 1. Create runtime-generated temp files
    # ----------------------------------------------------
    pdf_path = tmp_path / "input_pdf_runtime.pdf"
    img_path = tmp_path / "input_image_runtime.png"
    output_pdf = tmp_path / "merged_output_runtime.pdf"

    create_two_page_pdf(pdf_path)
    create_image_with_graphics(img_path)

    # ----------------------------------------------------
    # 2. Run the real merge function
    # ----------------------------------------------------
    import pdf_utils
    pdf_utils.merge_files([str(pdf_path), str(img_path)], str(output_pdf))

    # ----------------------------------------------------
    # 3. Verify output exists
    # ----------------------------------------------------
    assert output_pdf.exists(), "Merged PDF was not created"

    # ----------------------------------------------------
    # 4. Verify page count
    # ----------------------------------------------------
    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) == 3, "Merged PDF should contain 3 pages"

    # ----------------------------------------------------
    # 5. Verify text on the first two pages
    # ----------------------------------------------------
    page1_text = reader.pages[0].extract_text()
    page2_text = reader.pages[1].extract_text()

    assert "page 1" in page1_text
    assert "page 2" in page2_text

    # ----------------------------------------------------
    # 6. Verify the image page exists
    # ----------------------------------------------------
    page3_text = reader.pages[2].extract_text()
    assert page3_text is None or page3_text.strip() == ""

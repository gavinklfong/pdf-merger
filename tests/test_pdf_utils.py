import os
import pytest
from unittest.mock import patch, MagicMock
from subprocess import CalledProcessError

import pdf_utils


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------

import os
import pytest
from PIL import Image
import pdf_utils


@pytest.fixture
def fake_image(tmp_path):
    """Create a real temporary JPEG image."""
    path = tmp_path / "image.jpg"
    img = Image.new("RGB", (20, 20), color="white")
    img.save(path, "JPEG")
    return path


@pytest.fixture
def fake_corrupted_image(tmp_path):
    """Create a corrupted image file."""
    path = tmp_path / "corrupted.jpg"
    path.write_bytes(b"NOT_A_REAL_IMAGE")
    return path


@pytest.fixture
def fake_non_image(tmp_path):
    """Create a non-image file."""
    path = tmp_path / "file.txt"
    path.write_text("hello world")
    return path


@pytest.fixture
def fake_pdf(tmp_path):
    """Create a fake PDF file."""
    path = tmp_path / "file.pdf"
    path.write_bytes(b"%PDF-FAKE")
    return path


@pytest.fixture
def mock_img2pdf():
    with patch("img2pdf.convert", return_value=b"%PDF-FAKE") as m:
        yield m


@pytest.fixture
def mock_pdfreader():
    """Mock PdfReader so .pages is controllable."""
    with patch("pdf_utils.PdfReader") as m:
        m.return_value.pages = [MagicMock(), MagicMock(), MagicMock()]
        yield m


@pytest.fixture
def mock_pdfwriter():
    """Mock PdfWriter and return the instance."""
    with patch("pdf_utils.PdfWriter") as m:
        instance = MagicMock()
        m.return_value = instance
        yield instance


@pytest.fixture
def mock_tqdm():
    with patch("tqdm.tqdm") as m:
        bar = MagicMock()
        m.return_value = bar
        yield bar


# ---------------------------------------------------------
# convert_image_to_pdf
# ---------------------------------------------------------

def test_convert_image_to_pdf_success(fake_image, mock_img2pdf):
    pdf_path = pdf_utils.convert_image_to_pdf(str(fake_image), jpeg_quality=80)

    # PDF exists
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")

    # img2pdf.convert was called once
    mock_img2pdf.assert_called_once()

    # Extract the argument passed to img2pdf.convert
    temp_jpg_arg = mock_img2pdf.call_args[0][0]

    # It must be a temp JPEG file
    assert temp_jpg_arg.endswith(".jpg")

    # The temp JPEG should be deleted by the function
    assert not os.path.exists(temp_jpg_arg)

    os.remove(pdf_path)


def test_convert_image_to_pdf_corrupted(fake_corrupted_image):
    with pytest.raises(pdf_utils.ImageConversionError):
        pdf_utils.convert_image_to_pdf(str(fake_corrupted_image), jpeg_quality=80)


def test_convert_image_to_pdf_invalid_mime(fake_non_image):
    with pytest.raises(pdf_utils.ImageConversionError):
        pdf_utils.convert_image_to_pdf(str(fake_non_image), jpeg_quality=80)


def test_temp_jpeg_cleanup(fake_image, mock_img2pdf):
    pdf_path = pdf_utils.convert_image_to_pdf(str(fake_image), jpeg_quality=80)

    # Extract temp JPEG path
    temp_jpg_arg = mock_img2pdf.call_args[0][0]

    # Ensure cleanup happened
    assert not os.path.exists(temp_jpg_arg)

    os.remove(pdf_path)

# ---------------------------------------------------------
# optimize_pdf_with_ghostscript
# ---------------------------------------------------------

def test_optimize_pdf_no_ghostscript(fake_pdf, tmp_path):
    out = tmp_path / "out.pdf"

    with patch("shutil.which", return_value=None), \
         patch("shutil.copyfile") as mock_copy:

        pdf_utils.optimize_pdf_with_ghostscript(str(fake_pdf), str(out))
        mock_copy.assert_called_once_with(str(fake_pdf), str(out))


def test_optimize_pdf_with_ghostscript(fake_pdf, tmp_path):
    out = tmp_path / "out.pdf"

    with patch("shutil.which", return_value="/usr/bin/gs"), \
         patch("subprocess.run") as mock_run:

        pdf_utils.optimize_pdf_with_ghostscript(str(fake_pdf), str(out), quality="ebook")
        assert mock_run.called


def test_optimize_pdf_invalid_quality(fake_pdf, tmp_path):
    out = tmp_path / "out.pdf"

    with patch("shutil.which", return_value="/usr/bin/gs"):
        with pytest.raises(ValueError):
            pdf_utils.optimize_pdf_with_ghostscript(str(fake_pdf), str(out), quality="bad")


def test_optimize_pdf_ghostscript_failure(fake_pdf, tmp_path):
    out = tmp_path / "out.pdf"

    with patch("shutil.which", return_value="/usr/bin/gs"), \
         patch("subprocess.run", side_effect=CalledProcessError(1, "GS fail")), \
         patch("shutil.copyfile") as mock_copy:

        pdf_utils.optimize_pdf_with_ghostscript(str(fake_pdf), str(out))
        mock_copy.assert_called_once_with(str(fake_pdf), str(out))


# ---------------------------------------------------------
# count_total_pages
# ---------------------------------------------------------

def test_count_total_pages(fake_pdf, fake_image, mock_pdfreader):
    total = pdf_utils.count_total_pages([str(fake_pdf), str(fake_pdf), str(fake_image)])
    assert total == 3 + 3 + 1


# # ---------------------------------------------------------
# # merge_files
# # ---------------------------------------------------------

def test_merge_files(fake_pdf, fake_image, mock_pdfreader, mock_pdfwriter, mock_tqdm, tmp_path):
    # Fake image conversion
    with patch("pdf_utils.convert_image_to_pdf", return_value="temp.pdf"), \
         patch("pdf_utils.os.remove") as mock_remove:

        out = tmp_path / "merged.pdf"
        pdf_utils.merge_files([str(fake_pdf), str(fake_image)], str(out))

        # 3 pages from PDF + 3 pages from image-PDF
        assert mock_pdfwriter.add_page.call_count == 6

        mock_pdfwriter.write.assert_called_once_with(str(out))

        # temp file cleanup
        mock_remove.assert_called_with("temp.pdf")


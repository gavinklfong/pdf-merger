import os
import tempfile
import img2pdf
from pypdf import PdfReader, PdfWriter
from PIL import Image


def convert_image_to_pdf(path):
    """
    Converts an image (PNG/JPG/etc.) to a temporary PDF file.
    Returns the path to the temporary PDF.
    """

    ext = os.path.splitext(path)[1].lower()
    temp_files = []

    # STEP 1 — Convert PNG → JPG (img2pdf cannot handle PNG with alpha)
    if ext == ".png":
        img = Image.open(path).convert("RGB")
        fd, temp_jpg = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        img.save(temp_jpg, "JPEG", quality=80)
        temp_files.append(temp_jpg)
        image_to_convert = temp_jpg
    else:
        image_to_convert = path

    # STEP 2 — Convert JPG → PDF
    fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    with open(temp_pdf, "wb") as f:
        f.write(img2pdf.convert(image_to_convert))

    temp_files.append(temp_pdf)
    return temp_pdf, temp_files


def merge_files(file_paths, output_file):
    writer = PdfWriter()
    temp_files = []

    try:
        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()

            if ext == ".pdf":
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
                continue

            if ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]:
                temp_pdf, created = convert_image_to_pdf(path)
                temp_files.extend(created)

                reader = PdfReader(temp_pdf)
                for page in reader.pages:
                    writer.add_page(page)
                continue

            print(f"Skipping unsupported file: {path}")

        with open(output_file, "wb") as f:
            writer.write(f)

    finally:
        for tmp in temp_files:
            try:
                os.remove(tmp)
            except:
                pass

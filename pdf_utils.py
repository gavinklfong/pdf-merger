import os
import tempfile
import img2pdf
from PIL import Image
from pypdf import PdfReader, PdfWriter
import subprocess
import shutil
from tqdm import tqdm
import logging


def convert_image_to_pdf(path):
    """
    Converts an image (PNG/JPG/etc.) to a temporary PDF file.
    Returns the path to the temporary PDF.
    """

    ext = os.path.splitext(path)[1].lower()
    temp_jpg = None

    try:
        # STEP 1 — Convert PNG → JPG
        if ext == ".png":
            img = Image.open(path).convert("RGB")
            fd, temp_jpg = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            img.save(temp_jpg, "JPEG", quality=80)
            image_to_convert = temp_jpg
        else:
            image_to_convert = path

        # STEP 2 — Convert JPG → PDF
        fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        with open(temp_pdf, "wb") as f:
            f.write(img2pdf.convert(image_to_convert))

        return temp_pdf

    finally:
        # Cleanup temporary jpg file 
            try:
                os.remove(temp_jpg)
            except:
                pass


def optimize_pdf_with_ghostscript(input_pdf, output_pdf, quality="ebook"):
    """
    Optimize a PDF using Ghostscript.
    If Ghostscript is not installed, skip optimization and simply copy the input PDF.
    """

    # Try to locate Ghostscript
    gs = shutil.which("gs") or shutil.which("gswin64") or shutil.which("gswin32")

    if not gs:
        logging.warning("Ghostscript not found. Skipping optimization.")
        logging.debug(f"Copying input PDF to output: {output_pdf}")
        shutil.copyfile(input_pdf, output_pdf)
        return

    quality_map = {
        "screen": "/screen",
        "ebook": "/ebook",
        "printer": "/printer",
        "prepress": "/prepress",
    }

    if quality not in quality_map:
        raise ValueError(f"Invalid quality '{quality}'. Choose from: {list(quality_map.keys())}")

    cmd = [
        gs,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={quality_map[quality]}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_pdf}",
        input_pdf,
    ]

    try:
        subprocess.run(cmd, check=True)
        logging.debug(f"PDF optimized using Ghostscript ({quality}). Output: {output_pdf}")
    except subprocess.CalledProcessError as e:
        logging.error("Ghostscript optimization failed. Skip optimization.")
        logging.error(f"Reason: {e}")
        shutil.copyfile(input_pdf, output_pdf)

def count_total_pages(file_paths):
    total_pages = 0 
    for path in file_paths: 
        if path.lower().endswith(".pdf"): 
            total_pages += len(PdfReader(path).pages) 
        elif path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")): 
            total_pages += 1  # Each image counts as one page
    
    return total_pages


def merge_files(file_paths, output_file):
    writer = PdfWriter()
    temp_files = []

    total_pages = count_total_pages(file_paths)
    logging.info(f"Merging a total of {total_pages} pages from {len(file_paths)} files.")
    pbar = tqdm(total=total_pages, desc="Merging pages", unit="page")

    try:
        # Process each file
        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()

            # Handle PDF files
            if ext == ".pdf":
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
                    pbar.update(1)
                continue

            # Handle image files
            if ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]:
                temp_pdf = convert_image_to_pdf(path)
                temp_files.append(temp_pdf)

                reader = PdfReader(temp_pdf)
                for page in reader.pages:
                    writer.add_page(page)
                    pbar.update(1)
                continue

            logging.warning(f"Skipping unsupported file: {path}")

        pbar.close()

        writer.write(output_file)

    finally:
        # Cleanup temporary files
        for tmp in temp_files:
            try:
                os.remove(tmp)
            except:
                pass

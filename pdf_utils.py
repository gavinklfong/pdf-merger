import os
import tempfile
import img2pdf
import mimetypes
from PIL import Image, ImageOps, UnidentifiedImageError
from pypdf import PdfReader, PdfWriter
import subprocess
import shutil
import logging

COMPRESSION_MAP = {
    "highest": "screen",    # smallest file
    "high":    "ebook",     # strong compression
    "medium":  "printer",   # balanced
    "low":     "prepress",  # minimal compression
}


class ImageConversionError(Exception):
    pass

def validate_mime_type(path):

    mime, _ = mimetypes.guess_type(path)

    if not mime or not mime.startswith("image/"):
        raise ImageConversionError(
            f"Invalid MIME type for '{path}'. Expected an image, got '{mime}'."
        )

def convert_image_to_pdf(path, jpeg_quality):
    temp_jpg = None

    try:
        # STEP 0 — Validate MIME type
        validate_mime_type(path)

        # STEP 1 — Load image safely
        try:
            img = Image.open(path)
            img.load()
        except (UnidentifiedImageError, OSError) as e:
            raise ImageConversionError(f"Cannot read image '{path}': {e}")

        # STEP 2 — Apply EXIF orientation (critical for portrait images)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception as e:
            raise ImageConversionError(f"Failed to apply EXIF orientation: {e}")

        # STEP 3 — Convert to RGB for JPEG
        try:
            img = img.convert("RGB")
        except Exception as e:
            raise ImageConversionError(f"Failed to convert image to RGB: {e}")

        # STEP 4 — Save as JPEG with quality
        try:
            fd, temp_jpg = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            img.save(temp_jpg, "JPEG", quality=jpeg_quality)
        except Exception as e:
            raise ImageConversionError(f"Failed to save temporary JPEG: {e}")

        # STEP 5 — Convert JPEG → PDF
        try:
            fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)

            with open(temp_pdf, "wb") as f:
                f.write(img2pdf.convert(temp_jpg))

        except Exception as e:
            raise ImageConversionError(f"Failed to convert JPEG to PDF: {e}")

        return temp_pdf

    finally:
        if temp_jpg:
            try:
                os.remove(temp_jpg)
            except:
                pass


def optimize_pdf_with_ghostscript(input_pdf, output_pdf, quality="printer"):
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


def merge_files(file_paths, output_file, jpeg_quality=80, progress_callback=None):
    """
    progress_callback(event_dict):
        event_dict = {
            "pages_done": int,
            "message": str
        }
    """
    writer = PdfWriter()
    temp_files = []

    pages_done = 0

    if progress_callback is None:
        progress_callback = lambda event: None

    try:
        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()

            # PDF
            if ext == ".pdf":
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
                    pages_done += 1
                    progress_callback({
                        "pages_done": pages_done,
                        "message": f"Added page from {os.path.basename(path)}"
                    })
                continue

            # Image
            if ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]:
                temp_pdf = convert_image_to_pdf(path, jpeg_quality)
                temp_files.append(temp_pdf)

                reader = PdfReader(temp_pdf)
                for page in reader.pages:
                    writer.add_page(page)
                    pages_done += 1
                    progress_callback({
                        "pages_done": pages_done,
                        "message": f"Converted and added image {os.path.basename(path)}"
                    })
                continue

            logging.warning(f"Skipping unsupported file: {path}")

        progress_callback({
            "message": "Writing output PDF"
        })
        writer.write(output_file)

        progress_callback({
            "pages_done": pages_done,
            "message": "Merge complete"
        })

    finally:
        for tmp in temp_files:
            try:
                os.remove(tmp)
            except:
                pass


def merge_and_optimize(file_paths, output_file, jpeg_quality=80, compression_level=None, progress_callback=None):
    """
    Merge multiple PDF and image files into a single PDF.
    Optionally optimize the final PDF using Ghostscript.
    """

    if progress_callback is None:
        progress_callback = lambda event: None

    logging.debug(f"Starting merge of {len(file_paths)} files into {output_file}, jpeg_quality={jpeg_quality}, compression_level={compression_level}")

    # Create a temporary file for the merged PDF
    fd, temp_merged_pdf = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    try:
        # Merge files into the temporary PDF
        merge_files(file_paths, temp_merged_pdf, jpeg_quality=jpeg_quality, progress_callback=progress_callback)

        # Optimize if requested
        if compression_level and compression_level.lower() in COMPRESSION_MAP:
            progress_callback({
                "message": "Optimizing merged PDF"
            })
            optimize_pdf_with_ghostscript(temp_merged_pdf, output_file, quality=COMPRESSION_MAP[compression_level.lower()])
        else:
            logging.warning("No optimization quality specified or invalid quality. Skipping optimization.")
            shutil.move(temp_merged_pdf, output_file)

        progress_callback({
            "message": "Completed"
        })

    finally:
        # Cleanup temporary merged PDF if it still exists
        if os.path.exists(temp_merged_pdf):
            os.remove(temp_merged_pdf)
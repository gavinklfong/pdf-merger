import os
import tempfile
import img2pdf
from pypdf import PdfReader, PdfWriter
import subprocess
import shutil
from tqdm import tqdm


def convert_image_to_pdf(path):
    """
    Convert an image file (PNG/JPG/etc.) into a temporary PDF.
    Returns (temp_pdf_path, [temp_pdf_path]) for cleanup.
    """

    # Create a temporary PDF file
    fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    try:
        with open(temp_pdf, "wb") as f:
            f.write(img2pdf.convert(path))
    except Exception as e:
        print(f"Error converting image to PDF: {path} -> {e}")
        raise

    return temp_pdf


def optimize_pdf_with_ghostscript(input_pdf, output_pdf, quality="ebook"):
    """
    Optimize a PDF using Ghostscript.
    If Ghostscript is not installed, skip optimization and simply copy the input PDF.
    """

    # Try to locate Ghostscript
    gs = shutil.which("gs") or shutil.which("gswin64c") or shutil.which("gswin32c")

    if not gs:
        print("[INFO] Ghostscript not found. Skipping optimization.")
        print(f"[INFO] Copying input PDF to output: {output_pdf}")
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
        print(f"[INFO] PDF optimized using Ghostscript ({quality}). Output: {output_pdf}")
    except subprocess.CalledProcessError as e:
        print("[ERROR] Ghostscript optimization failed. Copying input PDF instead.")
        print(f"[ERROR] Reason: {e}")
        shutil.copyfile(input_pdf, output_pdf)

def create_progress_bar(file_paths):
    # Count total pages 
    total_pages = 0 
    for path in file_paths: 
        if path.lower().endswith(".pdf"): 
            total_pages += len(PdfReader(path).pages) 
        elif path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")): 
            total_pages += 1  # Each image counts as one page
    
    print(f"[INFO] Merging a total of {total_pages} pages from {len(file_paths)} files.")
    return tqdm(total=total_pages, desc="Merging pages", unit="page")


def merge_files(file_paths, output_file):
    writer = PdfWriter()
    temp_files = []

    pbar = create_progress_bar(file_paths)

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
                temp_files.extend(temp_pdf)

                reader = PdfReader(temp_pdf)
                for page in reader.pages:
                    writer.add_page(page)
                    pbar.update(1)
                continue

            print(f"[WARN] Skipping unsupported file: {path}")

        pbar.close()

        print("[INFO] Generating merged pdf")
        # Create a temporary PDF file for output
        fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        temp_files.extend(temp_pdf)

        with open(temp_pdf, "wb") as f:
            writer.write(f)
        
        # Optimize the merged PDF
        print("[INFO] Optimizing output pdf")
        optimize_pdf_with_ghostscript(temp_pdf, output_file)

    finally:
        # Cleanup temporary files
        for tmp in temp_files:
            try:
                os.remove(tmp)
            except:
                pass

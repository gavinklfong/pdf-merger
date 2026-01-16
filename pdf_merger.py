#!/usr/bin/env python3
import argparse
import os
import tempfile
import logging
from pdf_utils import merge_files, optimize_pdf_with_ghostscript


COMPRESSION_MAP = {
    "highest": "screen",    # smallest file
    "high":    "ebook",     # strong compression
    "medium":  "printer",   # balanced
    "low":     "prepress",  # minimal compression
}

logging.basicConfig( 
    level=logging.INFO, 
    format="[%(levelname)s] %(message)s" )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge multiple PDF files into a single output PDF."
    )

    parser.add_argument(
        "-i", "--input",
        nargs="+",
        required=True,
        help="List of input PDF file paths"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output PDF file path"
    )

    parser.add_argument(
        "-c", "--compression",
        choices=["highest", "high", "medium", "low"],
        default="medium",
        help="Compression quality for Ghostscript optimization (default: medium)"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Validate input files
    missing = [f for f in args.input if not os.path.isfile(f)]
    if missing:
        print("Error: The following input files do not exist:")
        for m in missing:
            print("  ", m)
        return

    # Ensure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.isdir(out_dir):
        print(f"Error: Output directory does not exist: {out_dir}")
        return

    # Create a temporary PDF file for output
    fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    try:
        logging.info("Generating merged pdf")
        merge_files(args.input, temp_pdf)
        
        # Optimize the merged PDF
        gs_quality = COMPRESSION_MAP[args.compression]
        logging.info("Optimizing output pdf")
        optimize_pdf_with_ghostscript(temp_pdf, args.output, quality=gs_quality)

    finally:
        # Cleanup temporary files
        try:
            os.remove(temp_pdf)
        except:
            pass



if __name__ == "__main__":
    main()

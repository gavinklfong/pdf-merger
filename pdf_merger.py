#!/usr/bin/env python3
import argparse
import os
from pdf_utils import merge_files


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

    merge_files(args.input, args.output)


if __name__ == "__main__":
    main()

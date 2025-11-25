from PyPDF2 import PdfMerger

def merge_pdfs(input_files, output_file):
    merger = PdfMerger()

    for pdf in input_files:
        merger.append(pdf)

    merger.write(output_file)
    merger.close()


if __name__ == "__main__":
    # List your PDF files in the order you want them merged
    pdf_list = [
        "sample1.pdf",
        "sample2.pdf",
        "sample3.pdf"
    ]

    merge_pdfs(pdf_list, "merged_output.pdf")
    print("PDFs merged successfully!")
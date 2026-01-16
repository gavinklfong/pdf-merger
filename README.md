# PDF Merger

> [!WARNING]
> This PDF merger relies open source libraries for PDF conversion and merging.<br>
> Accuracy of the output file is subject to quality of those libraries.<br>
> Please use it with caution and always verify the output content manually.


# Usage

Merge multiple PDF files into a single output PDF.

```
options:
-h, --help show this help message and exit
-i, --input INPUT [INPUT ...]    List of input PDF file paths
-o, --output OUTPUT              Output PDF file path
```

## Example

```
python merge_pdf.py -i /tmp/a.pdf /home/test/b.pdf -o /tmp/output.pdf
```

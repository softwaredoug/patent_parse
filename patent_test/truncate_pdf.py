#!/usr/bin/env python3
"""
Helper script to truncate PDFs to first two pages.
This keeps test assets small by only including the first two pages of patent PDFs.
"""

import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter


def truncate_pdf(input_path: str, output_path: str, max_pages: int = 2) -> None:
    """
    Extract the first N pages from a PDF and save to a new file.

    Args:
        input_path: Path to the input PDF file
        output_path: Path where the truncated PDF should be saved
        max_pages: Number of pages to extract (default: 2)
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)

    # Read the input PDF
    reader = PdfReader(input_file)
    total_pages = len(reader.pages)

    # Create a new PDF with only the first N pages
    writer = PdfWriter()
    pages_to_extract = min(max_pages, total_pages)

    for page_num in range(pages_to_extract):
        writer.add_page(reader.pages[page_num])

    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write the truncated PDF
    with open(output_file, 'wb') as f:
        writer.write(f)

    print(f"Extracted {pages_to_extract} of {total_pages} pages")
    print(f"Saved to: {output_path}")

    # Show file size reduction
    original_size = input_file.stat().st_size
    new_size = output_file.stat().st_size
    reduction = (1 - new_size / original_size) * 100
    print(f"Size reduction: {original_size:,} → {new_size:,} bytes ({reduction:.1f}% smaller)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python truncate_pdf.py <input_pdf> <output_pdf> [max_pages]")
        print("Example: python truncate_pdf.py input.pdf assets/input_truncated.pdf 2")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    truncate_pdf(input_pdf, output_pdf, max_pages)

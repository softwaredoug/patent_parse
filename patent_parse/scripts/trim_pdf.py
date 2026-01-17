#!/usr/bin/env python3
"""Trim a PDF to its first N pages to reduce test asset size."""

import argparse
import sys
from pathlib import Path

import fitz  # pymupdf


def trim_pdf(input_path: str, output_path: str | None = None, pages: int = 2) -> Path:
    """
    Extract the first N pages from a PDF and save to a new file.

    Args:
        input_path: Path to the source PDF
        output_path: Path for the trimmed PDF (defaults to overwriting input)
        pages: Number of pages to keep (default: 2)

    Returns:
        Path to the output file
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_file = Path(output_path) if output_path else input_file

    doc = fitz.open(input_path)
    total_pages = len(doc)

    if total_pages <= pages:
        print(f"PDF already has {total_pages} page(s), no trimming needed.")
        doc.close()
        return output_file

    # Create new document with only first N pages
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=0, to_page=pages - 1)

    # Save to output path
    new_doc.save(str(output_file))
    new_doc.close()
    doc.close()

    print(f"Trimmed {input_file.name}: {total_pages} -> {pages} pages")
    return output_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trim a PDF to its first N pages to reduce test asset size."
    )
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument(
        "-o", "--output",
        help="Output path (defaults to overwriting input file)"
    )
    parser.add_argument(
        "-p", "--pages",
        type=int,
        default=2,
        help="Number of pages to keep (default: 2)"
    )

    args = parser.parse_args()

    try:
        trim_pdf(args.input, args.output, args.pages)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error processing PDF: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

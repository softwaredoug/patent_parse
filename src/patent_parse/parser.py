"""Parser for extracting abstracts from patent PDFs."""

import re
import fitz  # pymupdf


def extract_abstract(pdf_path: str) -> str | None:
    """
    Extract the abstract from a patent PDF.

    Args:
        pdf_path: Path to the patent PDF file

    Returns:
        The abstract text if found, None otherwise
    """
    doc = fitz.open(pdf_path)

    # Get text from first few pages
    full_text = ""
    for page_num in range(min(3, len(doc))):
        page = doc[page_num]
        full_text += page.get_text() + "\n"

    doc.close()

    # Find the ABSTRACT section
    abstract_match = re.search(r'\bABSTRACT\b', full_text, re.IGNORECASE)
    if not abstract_match:
        return None

    # Extract text after ABSTRACT heading
    start_pos = abstract_match.end()
    remaining_text = full_text[start_pos:]

    # Split into lines and collect abstract text
    lines = remaining_text.split('\n')
    abstract_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Stop at section headers or reference markers
        if re.match(r'^(\d+\s+)?Claims?\s*,', line, re.IGNORECASE):
            break
        if re.match(r'^(FIELD|BACKGROUND|BRIEF DESCRIPTION|DETAILED DESCRIPTION)', line, re.IGNORECASE):
            break
        if re.match(r'^References Cited', line, re.IGNORECASE):
            break
        if re.match(r'^\(\s*\d+\s*\)', line):  # Patent classification codes like (51), (52)
            break

        abstract_lines.append(line)

    if not abstract_lines:
        return None

    # Join lines and clean up
    abstract = ' '.join(abstract_lines)

    # Remove common metadata patterns
    abstract = re.sub(r'\(\s*Continued\s*\)', '', abstract, flags=re.IGNORECASE)
    abstract = re.sub(r'\(\s*\d{4}\.\d{2}\s*\)', '', abstract)  # Remove (2014.01) style codes
    abstract = re.sub(r'\(\s*\d+\s*\)$', '', abstract)  # Remove trailing numbers in parens

    # Clean up multiple spaces
    abstract = re.sub(r'\s+', ' ', abstract).strip()

    # Fix spacing around punctuation (e.g., "cells ," -> "cells,")
    abstract = re.sub(r'\s+([,;.!?])', r'\1', abstract)

    return abstract if abstract else None

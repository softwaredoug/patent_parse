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

    # Extract text from first page using smart clipping
    # Find "ABSTRACT" and clip to its column (usually right side)
    page = doc[0]
    abstract_locations = page.search_for("ABSTRACT")

    if abstract_locations:
        # Get the first match
        abstract_rect = abstract_locations[0]

        # Detect if this looks like a multi-column layout
        # If abstract is > 55% across page, assume multi-column (abstract in right column)
        abstract_ratio = abstract_rect.x0 / page.rect.width

        if abstract_ratio > 0.55:
            # Multi-column: clip from just left of abstract to right edge
            # Start 200 points left of ABSTRACT to catch full abstract text
            clip_x0 = max(0, abstract_rect.x0 - 200)
            clip_rect = fitz.Rect(clip_x0, 0, page.rect.width, page.rect.height)
            full_text = page.get_text(clip=clip_rect) + "\n"
        else:
            # Single column: use full page
            full_text = page.get_text() + "\n"
    else:
        # Fallback: use full page if ABSTRACT not found
        full_text = page.get_text() + "\n"

    # Get full text from remaining pages (abstracts sometimes continue)
    for page_num in range(1, min(3, len(doc))):
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

        # Skip obvious non-abstract content
        # Classification codes like "32Of 138" or "320/109" or "B60L 50/64"
        if re.match(r'^\d+[Oo]f\s+\d+', line) or re.match(r'^\d+/\d+', line):
            continue
        if re.match(r'^[A-Z]{1,4}\d+[A-Z]?\s+\d', line):  # Patent class codes
            continue
        # Lines that are mostly numbers and spaces (diagram labels)
        if re.match(r'^[\d\s\-\(\)]+$', line) and len(line) > 3:
            continue
        # Lines with many dots (likely table of contents or references)
        if line.count('.') > 5:
            continue
        # Page markers
        if re.search(r'Page\s+\d+', line, re.IGNORECASE):
            continue
        # Search history markers
        if re.search(r'search history', line, re.IGNORECASE):
            continue
        # Single or two letter lines (likely noise from multi-column)
        if len(line) <= 2:
            continue
        # Common noise words from citations/references
        if line in ['Cited', 'CITED', 'OCUMENTS', 'DOCUMENTS', 'ed', 'ued']:
            continue

        abstract_lines.append(line)

    if not abstract_lines:
        return None

    # Join lines, handling split words at line breaks
    # If a line ends with a word fragment and next line starts with another fragment,
    # join them without space (split word), otherwise add space
    processed_lines = []
    for i, line in enumerate(abstract_lines):
        if i > 0 and processed_lines:
            prev_line = processed_lines[-1]
            # Get the last word of the previous line
            last_word_match = re.search(r'(\S+)\s*$', prev_line)
            # Get the first word of the current line
            first_word_match = re.match(r'^(\S+)', line)

            if last_word_match and first_word_match:
                last_word = last_word_match.group(1)
                first_word = first_word_match.group(1)

                # Check if this looks like a split word:
                # Case 1: Fragment + word (e.g., "effi"+"ciency", "elec"+"tric")
                # - Last word is 3-4 chars, first word is 4-7 chars
                # - Combined length 8-11 chars
                # Case 2: Word + suffix (e.g., "charg"+"ing", "start"+"ing")
                # - Last word is 5 chars, first word is 3 chars (common suffixes)
                # - Combined length 8 chars
                split_word = False
                if (3 <= len(last_word) <= 4 and
                    4 <= len(first_word) <= 7 and
                    last_word[-1].islower() and
                    first_word[0].islower() and
                    not re.search(r'[,;.!?]$', last_word) and
                    8 <= len(last_word + first_word) <= 11):
                    split_word = True
                elif (len(last_word) == 5 and
                      len(first_word) == 3 and
                      last_word[-1].islower() and
                      first_word[0].islower() and
                      not re.search(r'[,;.!?]$', last_word) and
                      first_word in ['ing', 'tion', 'ous', 'ent', 'ant', 'ity']):
                    split_word = True

                if split_word:
                    # This looks like a split word - join without space
                    processed_lines[-1] = prev_line + line
                    continue
        processed_lines.append(line)

    abstract = ' '.join(processed_lines)

    # Remove common metadata patterns
    abstract = re.sub(r'\(\s*Continued\s*\)', '', abstract, flags=re.IGNORECASE)
    abstract = re.sub(r'\(\s*\d{4}\.\d{2}\s*\)', '', abstract)  # Remove (2014.01) style codes
    abstract = re.sub(r'\(\s*\d+\s*\)$', '', abstract)  # Remove trailing numbers in parens

    # Clean up multiple spaces
    abstract = re.sub(r'\s+', ' ', abstract).strip()

    # Fix spacing around punctuation (e.g., "cells ," -> "cells,")
    abstract = re.sub(r'\s+([,;.!?])', r'\1', abstract)

    # Fix spaces around hyphens (e.g., "bi - stable" -> "bi-stable")
    abstract = re.sub(r'(\w)\s+-\s+(\w)', r'\1-\2', abstract)

    return abstract if abstract else None

"""Parser for extracting abstracts from patent PDFs."""

import re
import fitz  # pymupdf


def _extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from the first few pages of a patent PDF.

    Uses smart clipping for multi-column layouts to focus on the abstract section.

    Args:
        pdf_path: Path to the patent PDF file

    Returns:
        Extracted text from pages 1-3
    """
    doc = fitz.open(pdf_path)

    # Extract text from first page using smart clipping
    page = doc[0]
    abstract_locations = page.search_for("ABSTRACT")

    if abstract_locations:
        abstract_rect = abstract_locations[0]
        abstract_ratio = abstract_rect.x0 / page.rect.width

        if abstract_ratio > 0.55:
            # Multi-column: clip from just left of abstract to right edge
            clip_x0 = max(0, abstract_rect.x0 - 200)
            clip_rect = fitz.Rect(clip_x0, 0, page.rect.width, page.rect.height)
            full_text = page.get_text(clip=clip_rect) + "\n"
        else:
            # Single column: use full page
            full_text = page.get_text() + "\n"
    else:
        # Fallback: use full page if ABSTRACT not found
        full_text = page.get_text() + "\n"

    # Get text from remaining pages (abstracts sometimes continue)
    for page_num in range(1, min(3, len(doc))):
        page = doc[page_num]
        full_text += page.get_text() + "\n"

    doc.close()
    return full_text


def _find_abstract_section(text: str) -> str | None:
    """
    Find and extract the text after the ABSTRACT heading.

    Args:
        text: Full text from PDF

    Returns:
        Text after ABSTRACT heading, or None if not found
    """
    abstract_match = re.search(r'\bABSTRACT\b', text, re.IGNORECASE)
    if not abstract_match:
        return None

    return text[abstract_match.end():]


def _should_stop_collecting(line: str) -> bool:
    """
    Check if a line indicates the end of the abstract section.

    Args:
        line: Line to check

    Returns:
        True if this line marks the end of abstract
    """
    # Section headers
    if re.match(r'^(\d+\s+)?Claims?\s*,', line, re.IGNORECASE):
        return True
    if re.match(r'^(FIELD|BACKGROUND|BRIEF DESCRIPTION|DETAILED DESCRIPTION)', line, re.IGNORECASE):
        return True
    if re.match(r'^References Cited', line, re.IGNORECASE):
        return True

    # Patent classification codes like (51), (52)
    if re.match(r'^\(\s*\d+\s*\)', line):
        return True

    # "X Claims, Y Drawing Sheets" marker
    if re.search(r'\d+\s+Claims?\s*,\s*\d+\s+Drawing\s+Sheets?', line, re.IGNORECASE):
        return True

    return False


def _is_noise_line(line: str) -> bool:
    """
    Check if a line is noise/non-abstract content.

    Args:
        line: Line to check

    Returns:
        True if line should be skipped
    """
    # Classification codes like "32Of 138" or "320/109" or "B60L 50/64"
    if re.match(r'^\d+[Oo]f\s+\d+', line) or re.match(r'^\d+/\d+', line):
        return True
    if re.match(r'^[A-Z]{1,4}\d+[A-Z]?\s+\d', line):
        return True

    # Lines that are mostly numbers and spaces (diagram labels)
    if re.match(r'^[\d\s\-\(\)]+$', line) and len(line) > 3:
        return True

    # Lines with many dots (likely table of contents or references)
    if line.count('.') > 5:
        return True

    # Page markers
    if re.search(r'Page\s+\d+', line, re.IGNORECASE):
        return True

    # Search history markers
    if re.search(r'search history', line, re.IGNORECASE):
        return True

    # Single or two letter lines (likely noise from multi-column)
    if len(line) <= 2:
        return True

    # Common noise words from citations/references
    if line in ['Cited', 'CITED', 'OCUMENTS', 'DOCUMENTS', 'ed', 'ued']:
        return True

    # Author names (e.g., "Smith et al.", "Jones, Jr.")
    if re.search(r'\bet\s+al\.?\b', line, re.IGNORECASE):
        return True
    if re.search(r',\s+(Jr\.?|Sr\.?)\s*$', line, re.IGNORECASE):
        return True

    # Short lowercase fragments (likely split author names)
    if len(line) < 20 and line.islower():
        return True

    # Strange patterns like "coni'i'." or standalone numbers
    if re.match(r'^[a-z]{2,8}\'[a-z]\'\.\"?\s*\d+', line):
        return True

    # Diagram-like text: single capitalized words
    if len(line) < 25 and re.match(r'^[A-Z][a-z]+$', line):
        return True

    # Very short capitalized phrases (unless they look like abstract text)
    if len(line) < 20 and line.count(' ') <= 2 and re.match(r'^[A-Z]', line):
        if not re.search(r'[a-z]{3,}.*[a-z]{3,}', line):
            return True

    # Diagram labels (multiple question marks)
    if line.count('?') > 2 or line.count('???') > 0:
        return True

    return False


def _handle_continued_marker(line: str) -> tuple[str | None, bool]:
    """
    Handle the (Continued) marker that indicates abstract continues on next page.

    Args:
        line: Line that may contain (Continued) marker

    Returns:
        Tuple of (cleaned_line, found_continued_marker)
    """
    if re.search(r'\(\s*Continued\s*\)', line, re.IGNORECASE):
        # Remove (Continued) and everything after it
        cleaned = re.sub(r'\(\s*Continued\s*\).*', '', line, flags=re.IGNORECASE).strip()
        return (cleaned if cleaned else None, True)
    return (line, False)


def _should_resume_after_continued(line: str) -> bool:
    """
    Check if a line indicates we should resume collecting after (Continued).

    Args:
        line: Line to check

    Returns:
        True if we should resume collecting
    """
    # Continuation text typically starts with lowercase and is substantial
    if re.match(r'^[a-z]', line) and len(line) > 30:
        return True

    # Page marker indicates start of new page
    if re.match(r'^Page\s+\d+', line, re.IGNORECASE):
        return True

    return False


def _collect_abstract_lines(text: str) -> list[str]:
    """
    Collect abstract lines from text, filtering out noise.

    Args:
        text: Text after ABSTRACT heading

    Returns:
        List of abstract lines
    """
    lines = text.split('\n')
    abstract_lines = []
    seen_continued = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Handle (Continued) marker
        cleaned_line, found_continued = _handle_continued_marker(line)
        if found_continued:
            seen_continued = True
            if cleaned_line:
                abstract_lines.append(cleaned_line)
            continue

        # If we've seen (Continued), wait for continuation
        if seen_continued:
            if _should_resume_after_continued(line):
                seen_continued = False
                if not re.match(r'^Page\s+\d+', line, re.IGNORECASE):
                    # Resume with this line (unless it's just a page marker)
                    pass
                else:
                    continue
            else:
                # Skip lines between (Continued) and actual continuation
                continue

        # Check if we've reached the end of abstract
        if _should_stop_collecting(line):
            break

        # Skip noise lines
        if _is_noise_line(line):
            continue

        abstract_lines.append(line)

    return abstract_lines


def _is_split_word(last_word: str, first_word: str) -> bool:
    """
    Determine if two words appear to be parts of a split word.

    PDFs sometimes break words across lines (e.g., "effi" + "ciency").

    Args:
        last_word: Last word of previous line
        first_word: First word of current line

    Returns:
        True if these appear to be a split word
    """
    # Case 1: Fragment + word (e.g., "effi"+"ciency", "elec"+"tric")
    if (3 <= len(last_word) <= 4 and
        4 <= len(first_word) <= 7 and
        last_word[-1].islower() and
        first_word[0].islower() and
        not re.search(r'[,;.!?]$', last_word) and
        8 <= len(last_word + first_word) <= 11):
        return True

    # Case 2: Word + suffix (e.g., "charg"+"ing", "start"+"ing")
    if (len(last_word) == 5 and
        len(first_word) == 3 and
        last_word[-1].islower() and
        first_word[0].islower() and
        not re.search(r'[,;.!?]$', last_word) and
        first_word in ['ing', 'tion', 'ous', 'ent', 'ant', 'ity']):
        return True

    return False


def _join_split_words(lines: list[str]) -> str:
    """
    Join lines together, handling split words at line breaks.

    Args:
        lines: List of abstract lines

    Returns:
        Joined text with split words fixed
    """
    processed_lines = []

    for i, line in enumerate(lines):
        if i > 0 and processed_lines:
            prev_line = processed_lines[-1]

            # Get the last word of previous line and first word of current line
            last_word_match = re.search(r'(\S+)\s*$', prev_line)
            first_word_match = re.match(r'^(\S+)', line)

            if last_word_match and first_word_match:
                last_word = last_word_match.group(1)
                first_word = first_word_match.group(1)

                if _is_split_word(last_word, first_word):
                    # Join without space (split word)
                    processed_lines[-1] = prev_line + line
                    continue

        processed_lines.append(line)

    return ' '.join(processed_lines)


def _clean_abstract_text(text: str) -> str:
    """
    Clean up the abstract text by removing metadata and fixing formatting.

    Args:
        text: Raw abstract text

    Returns:
        Cleaned abstract text
    """
    # Remove common metadata patterns
    text = re.sub(r'\(\s*Continued\s*\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(\s*\d{4}\.\d{2}\s*\)', '', text)  # Remove (2014.01) style codes
    text = re.sub(r'\(\s*\d+\s*\)$', '', text)  # Remove trailing numbers in parens

    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Fix spacing around punctuation
    text = re.sub(r'\s+([,;.!?])', r'\1', text)

    # Fix spaces around hyphens (e.g., "bi - stable" -> "bi-stable")
    text = re.sub(r'(\w)\s+-\s+(\w)', r'\1-\2', text)

    return text


def extract_abstract(pdf_path: str) -> str | None:
    """
    Extract the abstract from a patent PDF.

    Args:
        pdf_path: Path to the patent PDF file

    Returns:
        The abstract text if found, None otherwise
    """
    # Extract text from PDF
    full_text = _extract_text_from_pdf(pdf_path)

    # Find the abstract section
    abstract_text = _find_abstract_section(full_text)
    if not abstract_text:
        return None

    # Collect abstract lines, filtering noise
    abstract_lines = _collect_abstract_lines(abstract_text)
    if not abstract_lines:
        return None

    # Join lines, handling split words
    abstract = _join_split_words(abstract_lines)

    # Clean up the text
    abstract = _clean_abstract_text(abstract)

    return abstract if abstract else None

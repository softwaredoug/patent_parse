"""Tests for patent PDF abstract extraction."""

import re
import pytest
from patent_parse import extract_abstract


def normalize_text(text):
    """Normalize text for lenient comparison."""
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()


def abstracts_match(expected, actual):
    """Check if abstracts match with lenient comparison."""
    # Normalize both
    norm_expected = normalize_text(expected)
    norm_actual = normalize_text(actual)

    # Check if normalized expected is substantially present in actual
    # Split into words and check overlap
    expected_words = set(norm_expected.split())
    actual_words = set(norm_actual.split())

    # Calculate overlap - at least 80% of expected words should be in actual
    if not expected_words:
        return False

    overlap = len(expected_words & actual_words)
    overlap_ratio = overlap / len(expected_words)

    # Also check for substring match after normalization
    substring_match = (norm_expected in norm_actual or
                      norm_actual in norm_expected or
                      overlap_ratio >= 0.8)

    return substring_match


# Table of patent PDFs and their expected abstracts
PATENT_TEST_CASES = [
    {
        "patent_id": "US11394072",
        "pdf_path": "tests/assets/US11394072.pdf",
        "expected_abstract": (
            "A lithium ion battery module includes a housing having a "
            "thermally conductive base and a cell assembly disposed within "
            "the housing and comprising pouch battery cells, a plurality of "
            "layers interleaved with the pouch battery cells, and a pair of "
            "end plates disposed on opposite ends of the cell assembly to "
            "compress the pouch battery cells. The battery cells are held "
            "within the cell assembly by cell frames. Each cell frame is "
            "formed from two frame pieces. The plurality of layers comprises "
            "a plurality of foam sheets and a plurality of thermally conductive "
            "sheets. The foam sheets are configured to allow swelling of the "
            "pouch battery cells while enabling a substantially constant level "
            "of compression of the pouch battery cells by the pair of end plates. "
            "The thermally conductive sheets conduct heat from the battery cells "
            "toward the thermally conductive base of the housing."
        ),
    },
    {
        "patent_id": "US11190026",
        "pdf_path": "tests/assets/US11190026.pdf",
        "expected_abstract": (
            "A 12 volt automotive battery system includes a first battery coupled to an "
            "electrical system, and the first battery includes a first battery chemistry. "
            "Further, the 12 volt automotive battery system includes a second battery coupled "
            "in parallel with the first battery and selectively coupled to the electrical system "
            "via a bi-stable relay. The second battery includes a second battery chemistry that "
            "has a higher coulombic efficiency than the first battery chemistry. Additionally, "
            "the bi-stable relay couples the second battery to the electrical system during "
            "regenerative braking to enable the second battery to capture a majority of the power "
            "generated during regenerative braking. Furthermore, the bi-stable relay maintains a "
            "coupling of the second battery to the electrical system when the vehicle transitions "
            "from a key-on position to a key-off position."
        ),
    },
    {
        "patent_id": "US8427103",
        "pdf_path": "tests/assets/US8427103.pdf",
        "expected_abstract": (
            "The present invention provides a charging device for an electric vehicle with which "
            "optimal charging can be performed reliably when charging a storage device of the "
            "electric vehicle, without performing fast charging and normal charging at the same time."
        ),
    },
]


@pytest.mark.parametrize(
    "test_case",
    PATENT_TEST_CASES,
    ids=[case["patent_id"] for case in PATENT_TEST_CASES],
)
def test_extract_abstract_from_patents(test_case):
    """Test abstract extraction from patent PDFs."""
    pdf_path = test_case["pdf_path"]
    expected_abstract = test_case["expected_abstract"]

    abstract = extract_abstract(pdf_path)

    assert abstract is not None, f"Abstract should be extracted from {test_case['patent_id']}"
    assert abstracts_match(expected_abstract, abstract), \
        f"Expected abstract not found in {test_case['patent_id']}.\n\nExpected:\n{expected_abstract}\n\nGot:\n{abstract}"

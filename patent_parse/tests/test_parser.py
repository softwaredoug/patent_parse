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
    {
        "patent_id": "US9277756",
        "pdf_path": "tests/assets/US9277756.pdf",
        "expected_abstract": (
            "Methods for preparing cheese are provided that involve combining a slurry with a cheese "
            "precursor to form an admixture that is subsequently processed to form the cheese product. "
            "The slurry typically includes a liquid such as water, milk and/or cream and one or more "
            "ingredients that are useful for inclusion in the final cheese product. Systems for preparing "
            "such slurries and cheese products are also provided."
        ),
    },
    {
        "patent_id": "US11029680",
        "pdf_path": "tests/assets/US11029680.pdf",
        "expected_abstract": (
            "Methods and systems for a monitoring system for data collection in an industrial environment "
            "including a data collector communicatively coupled to a plurality of input channels connected "
            "to data collection points operatively coupled to at least one of an oil production component "
            "or gas production component; a data storage structured to store a plurality of diagnostic "
            "frequency band ranges for the at least one of an oil production component or gas production "
            "component; a data acquisition circuit structured to interpret a plurality of detection values "
            "from the plurality of input channels, and a data analysis circuit structured to analyze the "
            "plurality of detection values to determine measured frequency band data and compare the "
            "measured frequency band data to the plurality of diagnostic frequency band ranges, and to "
            "diagnose an operational parameter of the least one of an oil production component or gas "
            "production component in response to the comparison."
        ),
    },
    {
        "patent_id": "CN104766014B",
        "pdf_path": "tests/assets/CN104766014B.pdf",
        "image_based": True,  # Scanned PDF, no text layer - requires OCR
        "expected_abstract": (
            "Disclosed herein are synthetic leathers, artificial epidermal layers, artificial dermal "
            "layers, layered structures, products produced therefrom and methods of producing the same."
        ),
    },
    {
        "patent_id": "US10535362",
        "pdf_path": "tests/assets/US10535362.pdf",
        "expected_abstract": (
            "Signals are received from audio pickup channels that contain signals from multiple sound "
            "sources. The audio pickup channels may include one or more microphones and one or more "
            "accelerometers. Signals representative of multiple sound sources are generated using a "
            "blind source separation algorithm. It is then determined which of those signals is deemed "
            "to be a voice signal and which is deemed to be a noise signal. The output noise signal "
            "may be scaled to match a level of the output voice signal, and a clean speech signal is "
            "generated based on the output voice signal and the scaled noise signal. Other aspects "
            "are described."
        ),
    },
    {
        "patent_id": "US11363389",
        "pdf_path": "tests/assets/US11363389.pdf",
        "expected_abstract": (
            "A hearing device comprises an ITE-part adapted for being located at or in an ear canal "
            "of the user comprising a housing comprising a seal towards walls or the ear canal, the "
            "ITE part comprising at least two microphones located outside the seal and facing the "
            "environment, and at least one microphone located inside the seal and facing the ear drum. "
            "The hearing device may comprise a beamformer filter connected to said at least three "
            "microphones comprising a first beamformer for spatial filtering said sound in the "
            "environment based on input signals from said at least two microphones facing the "
            "environment, and a second beamformer for spatial filtering sound reflected from the ear "
            "drum based on said at least one electric input signal from said at least one microphone "
            "facing the ear drum and at least one of said input signals from said at least two "
            "microphones facing the environment."
        ),
    },
    {
        "patent_id": "US11762912",
        "pdf_path": "tests/assets/US11762912.pdf",
        "image_based": True,  # Scanned PDF, no text layer - requires OCR
        "expected_abstract": (
            "The invention provides a system and method for providing ttx-based categorization "
            "services and a categorized commonplace of shared information. Currency of the contents "
            "is improved by a process called conjuring/concretizing wherein users' thoughts are "
            "rapidly infused into the Map. As a new idea is sought, a goal is created for a search. "
            "After the goal idea is found, a ttx is concretized and categorized. The needs met by "
            "such a Map are prior art searching, competitive environmental scanning, competitive "
            "analysis study repository management and reuse, innovation gap analysis indication, "
            "novelty checking, technology value prediction, investment area indication and planning, "
            "and product technology comparison and feature planning."
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
    if test_case.get("image_based"):
        pytest.skip(f"{test_case['patent_id']} is image-based/scanned (requires OCR)")

    pdf_path = test_case["pdf_path"]
    expected_abstract = test_case["expected_abstract"]

    abstract = extract_abstract(pdf_path)

    assert abstract is not None, f"Abstract should be extracted from {test_case['patent_id']}"
    assert abstracts_match(expected_abstract, abstract), \
        f"Expected abstract not found in {test_case['patent_id']}.\n\nExpected:\n{expected_abstract}\n\nGot:\n{abstract}"

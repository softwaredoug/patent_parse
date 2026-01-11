"""Tests for patent PDF abstract extraction."""

import pytest
from patent_parse import extract_abstract


def test_us11394072_abstract():
    """Test abstract extraction from US11394072 patent."""
    pdf_path = "tests/assets/US11394072.pdf"

    expected_abstract = (
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
    )

    abstract = extract_abstract(pdf_path)

    assert abstract is not None, "Abstract should be extracted"
    assert expected_abstract in abstract or abstract in expected_abstract, \
        f"Expected abstract not found. Got: {abstract}"

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
    {
        "patent_id": "US20090043621A1",
        "pdf_path": "tests/assets/US20090043621A1.pdf",
        "expected_abstract": (
            "The invention is an application for teams of information workers, their managers, "
            "and human resources professionals to evaluate and raise performance based on "
            "communication metrics and norms of behavior within a team. A model and management "
            "Web pages enable users to collectively set norms of behavior, communicate, make "
            "decisions, set roles and goals, receive evaluations according to their norms, and "
            "in other ways conduct interpersonal relations in a business context. Modules "
            "acquiring data from email and document management systems, groupware, directories, "
            "and other information sources are included. Said information is joined with the "
            "invention's internally generated data. An expert system generates observations and "
            "advice permitting the team to more appropriately deploy information, adhere more "
            "closely to its norms, and lessen stress caused by interpersonal friction. Management "
            "is provided a means of assessing teams, setting policies, and defining parametric "
            "ranges for norms."
        ),
    },
    {
        "patent_id": "US9545412",
        "pdf_path": "tests/assets/US9545412.pdf",
        "expected_abstract": (
            "This invention relates to a composition comprising an anti-HIV treatment and a "
            "treatment for side effects of said anti-HIV treatment in an HIV-infected patient. "
            "This invention is, for example, very useful in the treatment of side effects caused "
            "by certain anti-HIV treatments, for example premature aging and lipodystrophy, which "
            "can be caused by protease inhibitors or reverse transcriptase inhibitors. The "
            "composition of this invention includes at least one hydroxymethylglutaryl-coenzyme A "
            "(HMG-CoA) reductase inhibitor, at least one farnesyl-pyrophosphate synthase inhibitor, "
            "and at least one anti-HIV agent. One of the processes for treating an HIV-infected "
            "patient includes, in any order, the following steps: (i) administration of a mixture "
            "including at least one hydroxymethylglutaryl-coenzyme A (HMG-CoA) reductase inhibitor "
            "and at least one farnesyl-pyrophosphate synthase inhibitor and (ii) administration of "
            "an anti-HIV agent, in which the administrations are concomitant, successive or alternative."
        ),
    },
    {
        "patent_id": "US8432257",
        "pdf_path": "tests/assets/US8432257.pdf",
        "expected_abstract": (
            "Techniques are disclosed for writing data directly onto a product to record each "
            "ownership transfer. As a result, the product itself now carries a traceable, auditable, "
            "non-forgeable, non-repudiable proof of ownership (and, optionally, ownership history) "
            "that can be used in a variety of ways. This recorded ownership transfer information "
            "provides an electronic receipt, which may be used by the present owner to prove his or "
            "her ownership. (Optionally, other types of transfers may be recorded in addition to, or "
            "instead of, ownership transfers.) A transfer agent or registrar may create a unique "
            "transaction identifier to represent the transfer, and preferably creates a cryptographic "
            "signature over fields representing the transfer. This information may be recorded in a "
            "repository that is external from the product."
        ),
    },
    {
        "patent_id": "US12110498",
        "pdf_path": "tests/assets/US12110498.pdf",
        "image_based": True,  # Scanned PDF, no text layer - requires OCR
        "expected_abstract": (
            "Provided herein are compositions and methods of integrating one or more exogenous donor "
            "nucleic acids into one or more exogenous landing pads engineered into a host cell's "
            "genome. In certain embodiments, the exogenous landing pads and exogenous donor nucleic "
            "acids comprise standardized, compatible homology regions so that exogenous donor nucleic "
            "acids can integrate into any of the landing pads, independent of the genomic sequences "
            "surrounding the landing pads. In certain embodiments, the methods comprise contacting "
            "the host cell comprising landing pads with one or more exogenous donor nucleic acids, "
            "and a nuclease capable of causing a double-strand break within the landing pads, and "
            "recovering a host cell comprising one or more exogenous donor nucleic acids integrated "
            "in any of the landing pads."
        ),
    },
    {
        "patent_id": "US9753649",
        "pdf_path": "tests/assets/US9753649.pdf",
        "expected_abstract": (
            "Systems, methods and/or devices are used to enable tracking intermix of writes and "
            "un-map commands across power cycles. In one aspect, the method includes (1) receiving, "
            "at a storage device, a plurality of commands from a host, the storage device including "
            "non-volatile memory, (2) maintaining a log corresponding to write commands and un-map "
            "commands from the host, (3) maintaining a mapping table in volatile memory, the mapping "
            "table used to translate logical addresses to physical addresses, (4) saving the mapping "
            "table, on a scheduled basis that is independent of the un-map commands, to the "
            "non-volatile memory of the storage device, (5) saving the log to the non-volatile "
            "memory, and (6) upon power up of the storage device, rebuilding the mapping table from "
            "the saved mapping table in the non-volatile memory of the storage device and from the "
            "saved log in the non-volatile memory of the storage device."
        ),
    },
    {
        "patent_id": "US9795977",
        "pdf_path": "tests/assets/US9795977.pdf",
        "expected_abstract": (
            "An electrically-actuated variable pressure control system for use with flow-controlled "
            "liquid application systems. Direct acting solenoid valves are pulsed at varying "
            "frequencies and duty cycles to change the resistance to flow encountered by the "
            "flow-controlled liquid application system. This pulsing solenoid valve technique "
            "preserves a high degree of accuracy and uniformity through a wide range of pressure "
            "control. This wide range of pressure control indirectly allows the flow-controlled "
            "liquid application system to operate over a wider range of flow control, yielding "
            "indirect benefits to performance and productivity. When the solenoid valves are "
            "attached to pressure-atomization spray nozzles, control over spray pattern and droplet "
            "size is further achieved."
        ),
    },
    {
        "patent_id": "US11151203",
        "pdf_path": "tests/assets/US11151203.pdf",
        "expected_abstract": (
            "Techniques for generating interest embedding vectors are disclosed. In some "
            "embodiments, a system/process/computer program product for generating interest "
            "embedding vectors includes aggregating a plurality of web documents associated with "
            "one or more entities, wherein the web documents are retrieved from a plurality of "
            "online content sources including one or more websites; selecting a plurality of tokens "
            "based on processing of the plurality of web documents; and generating embeddings of "
            "the selected tokens in an embedding space."
        ),
    },
    {
        "patent_id": "US11477246",
        "pdf_path": "tests/assets/US11477246.pdf",
        "expected_abstract": (
            "A technique involves modular storage of network service plan components and "
            "provisioning of same. A subset of the capabilities of a service design system can be "
            "granted to a sandbox system to enable customization of service plan offerings or "
            "other controls."
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

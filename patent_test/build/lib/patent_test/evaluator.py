"""
Patent Parser Evaluator

A black-box evaluator for patent PDF parsers.
Takes a parser function and returns accuracy score.
"""

import re
from pathlib import Path
from typing import Callable

import yaml


def _normalize(text: str) -> list[str]:
    """Normalize text for comparison: lowercase, remove punctuation, split into words."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.split()


def evaluate(parser_fn: Callable[[str], str]) -> float:
    """
    Evaluate a patent parser function against ground truth test cases.

    Args:
        parser_fn: A callable that takes a PDF path (str) and returns the extracted abstract (str).
                   The parser_fn will receive absolute paths to test PDF files.

    Returns:
        Accuracy score as a float from 0.0 to 1.0.
    """
    # Get paths relative to this package
    package_dir = Path(__file__).parent
    tests_path = package_dir / "tests.yml"

    with open(tests_path, "r") as f:
        data = yaml.safe_load(f)

    tests = data.get("tests", [])
    if not tests:
        return 0.0

    correct = 0
    for test in tests:
        # Convert relative paths to absolute paths based on package location
        pdf_path = test["path"]
        if not Path(pdf_path).is_absolute():
            pdf_path = str(package_dir / pdf_path)

        expected_abstract = test["abstract"]

        extracted_abstract = parser_fn(pdf_path)

        expected_normalized = _normalize(expected_abstract)
        extracted_normalized = _normalize(extracted_abstract)

        if expected_normalized == extracted_normalized:
            correct += 1

    return correct / len(tests)

"""
Patent Parser Evaluator

A black-box evaluator for patent PDF parsers.
Takes a parser function and returns accuracy score.
"""

import re
from pathlib import Path
from typing import Callable

import yaml


def _normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, remove punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return ' '.join(text.split())


def _levenshtein(s1: str, s2: str) -> float:
    """Calculate normalized Levenshtein distance between two strings.

    Returns a value from 0.0 (identical) to 1.0 (completely different).
    """
    if len(s1) == 0 and len(s2) == 0:
        return 0.0

    if len(s1) < len(s2):
        s1, s2 = s2, s1

    if len(s2) == 0:
        return 1.0

    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1] / max(len(s1), len(s2))


def evaluate(parser_fn: Callable[[str], str]) -> tuple[float, float]:
    """
    Evaluate a patent parser function against ground truth test cases.

    Args:
        parser_fn: A callable that takes a PDF path (str) and returns the extracted abstract (str).
                   The parser_fn will receive absolute paths to test PDF files.

    Returns:
        A tuple of (accuracy, avg_levenshtein_distance):
        - accuracy: float from 0.0 to 1.0 (percentage of exact matches)
        - avg_levenshtein_distance: float from 0.0 to 1.0 (0.0 = identical, 1.0 = completely different)
    """
    # Get paths relative to this package
    package_dir = Path(__file__).parent
    tests_path = package_dir / "tests.yml"

    with open(tests_path, "r") as f:
        data = yaml.safe_load(f)

    tests = data.get("tests", [])
    if not tests:
        return 0.0, 0.0

    correct = 0
    total_distance = 0
    for test in tests:
        # Convert relative paths to absolute paths based on package location
        pdf_path = test["path"]
        if not Path(pdf_path).is_absolute():
            pdf_path = str(package_dir / pdf_path)

        expected_abstract = test["abstract"]

        extracted_abstract = parser_fn(pdf_path)

        expected_normalized = _normalize(expected_abstract)
        extracted_normalized = _normalize(extracted_abstract)

        distance = _levenshtein(expected_normalized, extracted_normalized)
        total_distance += distance

        if expected_normalized == extracted_normalized:
            correct += 1

    accuracy = correct / len(tests)
    avg_distance = total_distance / len(tests)
    return accuracy, avg_distance

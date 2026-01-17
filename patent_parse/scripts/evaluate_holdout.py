#!/usr/bin/env python3
"""Evaluate parser accuracy against the held-out patent test set."""

from patent_parse import extract_abstract
from patent_test import evaluate


def safe_extract(pdf_path: str) -> str:
    """Extract abstract, returning empty string on failure."""
    result = extract_abstract(pdf_path)
    return result if result else ""


def main() -> None:
    accuracy, avg_distance = evaluate(safe_extract)
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Avg Levenshtein distance: {avg_distance:.1f}")


if __name__ == "__main__":
    main()

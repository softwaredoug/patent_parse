# Patent Test

A heldout test set for evaluating patent PDF parsing.

## Installation

Install this package in your parser project:

```bash
# Using uv
uv add --editable /path/to/patent_test

# Or using pip
pip install -e /path/to/patent_test
```

## Usage

Use this in your integration tests to evaluate your parser:

```python
from patent_test import evaluate

def my_parser(pdf_path: str) -> str:
    """Your parser implementation that extracts abstract from PDF."""
    # ... your parsing logic ...
    return extracted_abstract

# Run evaluation
accuracy = evaluate(my_parser)
print(f"Parser accuracy: {accuracy:.1%}")
```

The `evaluate()` function:
- Takes a callable with signature `Callable[[str], str]`
- Passes absolute paths to test PDF files to your parser
- Returns accuracy as a float from 0.0 to 1.0
- Compares normalized text (lowercase, no punctuation, whitespace-separated)

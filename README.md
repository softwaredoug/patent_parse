# Patent Parse

A Python library for parsing abstracts from patent PDFs downloaded from Google Scholar.

## Installation

```bash
uv add patent-parse
```

## Usage

```python
from patent_parse import extract_abstract

# Extract abstract from a patent PDF
abstract = extract_abstract("path/to/patent.pdf")
if abstract:
    print(abstract)
```

## Requirements

- Python >= 3.12
- pymupdf (fitz)

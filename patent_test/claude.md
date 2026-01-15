# Patent Parser Evaluator

This is a **Python** codebase.

## Scope

You only have permission to look in this `patent_test` directory. Do not access parent directories or other projects.

## Purpose

This project is a **black box evaluator** for patent parsers. You are intentionally walled off from the parser implementations being tested. Your role is to evaluate accuracy, not to help build parsers.

## Main Function

The evaluator takes as input:
- A Python callable with signature: `Callable[[str], str]` (accepts a PDF path, returns the extracted abstract)

The evaluator returns:
- An accuracy score as a percentage (% of abstracts correctly extracted)

## Test Assets

Store test patent PDFs and their expected abstracts (ground truth) in this directory. The evaluator compares parser output against ground truth to compute accuracy.

### Test Data Format

Test cases are defined in `src/patent_test/tests.yml` with the following structure:
```yaml
tests:
  - path: assets/US20180279539A1.pdf
    abstract: "The expected abstract text here..."
```

Note: Paths in `tests.yml` are relative to the package root (`src/patent_test/`).

### Adding New Patent PDFs

To keep test assets small, always truncate patent PDFs to their first two pages:

1. Download the patent PDF from the source (e.g., Google Patents)
2. Run the truncation script:
   ```bash
   python truncate_pdf.py downloaded.pdf src/patent_test/assets/PATENT_ID.pdf
   ```
3. Add the test case to `src/patent_test/tests.yml` with the correct abstract text

The `truncate_pdf.py` script extracts the first 2 pages and typically reduces file size by 80-90%.

## Project Structure

This package uses the modern **src layout**:
```
patent_test/                    # Project root
├── src/
│   └── patent_test/            # Importable package
│       ├── __init__.py
│       ├── evaluator.py
│       ├── tests.yml
│       └── assets/             # Test PDFs
├── pyproject.toml
├── truncate_pdf.py
└── README.md
```

Key configuration in `pyproject.toml`:
- `[tool.setuptools.packages.find]` - Tells setuptools to find packages in `src/`
- `[tool.setuptools.package-data]` - Ensures `tests.yml` and `assets/*.pdf` are included in distributions

## Testing Package Installation

When making changes to the package structure or configuration, test that the package installs correctly:

```bash
# Create isolated test environment
mkdir -p /tmp/patent_test_validation
cd /tmp/patent_test_validation

# Create test script
cat > test_import.py << 'EOF'
from patent_test import evaluate

def dummy_parser(pdf_path: str) -> str:
    return ""

accuracy = evaluate(dummy_parser)
print(f"✓ Package imported successfully")
print(f"✓ Accuracy: {accuracy:.1%}")
EOF

# Test with non-editable install (verifies data files are included)
python3 -m venv .venv
source .venv/bin/activate
pip install /path/to/patent_test
python test_import.py

# Cleanup
deactivate
cd -
rm -rf /tmp/patent_test_validation
```

This verifies:
- Package installs without errors
- `from patent_test import evaluate` works
- Data files (`tests.yml` and PDFs) are included in the distribution
- `evaluate()` can find and read test files

## Guidelines

- Do not look at or assist with parser implementation code
- Focus only on building and maintaining the test harness and test data
- Keep ground truth abstracts accurate and well-formatted
- Report accuracy metrics objectively

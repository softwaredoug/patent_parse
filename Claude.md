# Claude Workflow for Patent Parse

## Project Goal

This library is designed to parse abstracts from patent PDFs, specifically those downloaded from Google Scholar. The goal is to accurately extract the abstract section from various patent PDF formats.

**Critical Requirement:** The parser must keep whole words together. PDFs sometimes split words across line breaks (e.g., "effi ciency" or "main tains"), and the parser must reconstruct these into complete words ("efficiency", "maintains"). This is essential for producing readable, usable abstracts.

## Development Workflow

The typical workflow for improving the parser follows a test-driven approach:

1. **User provides patent PDF URLs**: The user (Doug) shares URLs to patent PDFs that need to be tested.

2. **Download and extract abstract**:
   - Download the PDF to the `tests/assets/` folder (don't overwrite if it already exists)
   - Open the PDF and extract the abstract using the current parser
   - Review the extracted abstract to ensure it looks correct

3. **Create test case**:
   - Create a test in `tests/test_parser.py` with the expected abstract
   - The test should verify that the parser correctly extracts the abstract from that specific patent

4. **Run tests**:
   - Execute the test suite with `uv run pytest tests/ -v`
   - Identify any failures or issues

5. **Fix parser code**:
   - If tests fail, update the parser logic in `src/patent_parse/parser.py`
   - Address edge cases, improve pattern matching, or refine extraction logic
   - Re-run tests until they pass

6. **Iterate**:
   - Repeat this process with additional patent PDFs to improve robustness
   - Each new patent format may reveal new edge cases to handle

## Key Files

- `src/patent_parse/parser.py` - Core abstract extraction logic
- `tests/test_parser.py` - Test cases for various patent PDFs
- `tests/assets/` - Downloaded patent PDF files for testing

## Running Tests

```bash
uv run pytest tests/ -v
```

# Claude Workflow for Patent Parse

## Project Goal

This library is designed to parse abstracts from patent PDFs, specifically those downloaded from Google Scholar. The goal is to accurately extract the abstract section from various patent PDF formats.

**Critical Requirement:** The parser must keep whole words together. PDFs sometimes split words across line breaks (e.g., "effi ciency" or "main tains"), and the parser must reconstruct these into complete words ("efficiency", "maintains"). This is essential for producing readable, usable abstracts.

## Development Workflow

The typical workflow for improving the parser follows a test-driven approach:

1. **User provides patent PDF URLs with abstracts**: The user (Doug) shares URLs to patent PDFs along with their expected abstracts.

2. **For each PDF**:
   - Download the PDF to `tests/assets/` (skip if it already exists)
   - Trim to first 2 pages: `uv run python scripts/trim_pdf.py tests/assets/<patent>.pdf`
   - Create a test case in `tests/test_parser.py` with the provided expected abstract

3. **Run tests** (this repo only, not the holdout):
   - Execute `uv run pytest tests/ -v`
   - Focus on passing tests in this repo first; holdout scoring is secondary

4. **Fix parser code**:
   - If tests fail, update the parser logic in `src/patent_parse/parser.py`
   - Address edge cases, improve pattern matching, or refine extraction logic

5. **GOTO 3**: Repeat until all new patent tests pass

6. **Verify holdout did not degrade** (guards against overfitting):
   - Run `uv pip install --reinstall /Users/doug/ws/patent_parse/patent_test`
   - Run `uv run python scripts/evaluate_holdout.py`
   - If accuracy decreased, the fix may be overfitting to the test cases
   - If edit distance (Levenshtein) increased, this also points to overfitting
   - Rework the fix to be more general if holdout degraded

## Holdout Workflow

This workflow ensures the parser generalizes well and doesn't overfit to the test cases in this repo.

**Important:** Do NOT introspect the `patent_test` project in `.venv/lib/.../site-packages/`. That defeats the purpose of the holdout.

1. **Ensure all tests pass**:
   - Run `uv run pytest tests/ -v`
   - All tests in this repo must pass before proceeding

2. **Reinstall patent_test** (new tests may be added periodically):
   - Run `uv pip install --reinstall /Users/doug/ws/patent_parse/patent_test`

3. **Evaluate against holdout**:
   - Run `uv run python scripts/evaluate_holdout.py`
   - Note the current accuracy and avg Levenshtein distance
   - Accuracy ranges from 0-1, higher is better
   - Edit distance (Levenshtein) ranges from 0-1, lower is better

4. **Improve parser code**:
   - Make changes to `src/patent_parse/parser.py` to improve generalization
   - Focus on robust patterns, not test-specific fixes

5. **Verify tests still pass**:
   - Run `uv run pytest tests/ -v`
   - If any tests fail, fix before continuing

6. **Re-evaluate holdout**:
   - Run `uv run python scripts/evaluate_holdout.py`
   - Check if accuracy or avg Levenshtein distance improved

7. **GOTO 4**: Iterate to improve holdout metrics while keeping tests green

## Key Files

- `src/patent_parse/parser.py` - Core abstract extraction logic
- `tests/test_parser.py` - Test cases for various patent PDFs
- `tests/assets/` - Downloaded patent PDF files for testing
- `scripts/trim_pdf.py` - Helper to trim PDFs to first 2 pages
- `scripts/evaluate_holdout.py` - Evaluate parser against holdout set

## Running Tests

```bash
uv run pytest tests/ -v
```

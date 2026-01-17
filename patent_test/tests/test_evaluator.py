"""Tests for the patent parser evaluator."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from patent_test.evaluator import _levenshtein, _normalize, evaluate


class TestNormalize:
    """Tests for the _normalize function."""

    def test_lowercase(self):
        assert _normalize("HELLO WORLD") == "hello world"

    def test_removes_punctuation(self):
        assert _normalize("Hello, world!") == "hello world"

    def test_collapses_whitespace(self):
        assert _normalize("hello    world") == "hello world"

    def test_handles_newlines(self):
        assert _normalize("hello\nworld") == "hello world"

    def test_empty_string(self):
        assert _normalize("") == ""

    def test_complex_text(self):
        text = "A patent (US123) includes: sensors, motors, and controllers."
        expected = "a patent us123 includes sensors motors and controllers"
        assert _normalize(text) == expected


class TestLevenshtein:
    """Tests for the _levenshtein function (normalized 0-1 scale)."""

    def test_identical_strings(self):
        assert _levenshtein("hello", "hello") == 0.0

    def test_empty_strings(self):
        assert _levenshtein("", "") == 0.0

    def test_one_empty_string(self):
        # Completely different = 1.0
        assert _levenshtein("hello", "") == 1.0
        assert _levenshtein("", "world") == 1.0

    def test_single_insertion(self):
        # 1 edit out of 5 chars = 0.2
        assert _levenshtein("helo", "hello") == pytest.approx(1 / 5)

    def test_single_deletion(self):
        # 1 edit out of 5 chars = 0.2
        assert _levenshtein("hello", "helo") == pytest.approx(1 / 5)

    def test_single_substitution(self):
        # 1 edit out of 5 chars = 0.2
        assert _levenshtein("hello", "hallo") == pytest.approx(1 / 5)

    def test_multiple_edits(self):
        # 3 edits out of 7 chars (sitting is longer) = 3/7
        assert _levenshtein("kitten", "sitting") == pytest.approx(3 / 7)

    def test_completely_different(self):
        # 3 edits out of 3 chars = 1.0
        assert _levenshtein("abc", "xyz") == 1.0


class TestEvaluate:
    """Tests for the evaluate function."""

    @pytest.fixture
    def mock_tests_dir(self):
        """Create a temporary directory with mock test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            assets_dir = tmpdir / "assets"
            assets_dir.mkdir()

            # Create empty mock PDF files
            (assets_dir / "patent1.pdf").touch()
            (assets_dir / "patent2.pdf").touch()
            (assets_dir / "patent3.pdf").touch()

            yield tmpdir

    def test_perfect_accuracy(self, mock_tests_dir):
        """Test 100% accuracy when parser returns exact matches."""
        tests_data = {
            "tests": [
                {"path": "assets/patent1.pdf", "abstract": "This is abstract one."},
                {"path": "assets/patent2.pdf", "abstract": "This is abstract two."},
            ]
        }

        tests_yml = mock_tests_dir / "tests.yml"
        with open(tests_yml, "w") as f:
            yaml.dump(tests_data, f)

        def mock_parser(pdf_path: str) -> str:
            if "patent1" in pdf_path:
                return "This is abstract one."
            elif "patent2" in pdf_path:
                return "This is abstract two."
            return ""

        with patch("patent_test.evaluator.Path") as mock_path:
            mock_path.return_value.parent = mock_tests_dir
            mock_path.return_value.is_absolute.return_value = False
            mock_path.__truediv__ = lambda self, other: mock_tests_dir / other

            # Patch __file__ location
            with patch("patent_test.evaluator.__file__", str(mock_tests_dir / "evaluator.py")):
                accuracy, avg_distance = evaluate(mock_parser)

        assert accuracy == 1.0
        assert avg_distance == 0.0

    def test_zero_accuracy(self, mock_tests_dir):
        """Test 0% accuracy when parser returns wrong results."""
        tests_data = {
            "tests": [
                {"path": "assets/patent1.pdf", "abstract": "Expected abstract"},
                {"path": "assets/patent2.pdf", "abstract": "Another expected"},
            ]
        }

        tests_yml = mock_tests_dir / "tests.yml"
        with open(tests_yml, "w") as f:
            yaml.dump(tests_data, f)

        def mock_parser(pdf_path: str) -> str:
            return "completely wrong output"

        with patch("patent_test.evaluator.__file__", str(mock_tests_dir / "evaluator.py")):
            accuracy, avg_distance = evaluate(mock_parser)

        assert accuracy == 0.0
        assert 0 < avg_distance <= 1.0

    def test_partial_accuracy(self, mock_tests_dir):
        """Test 50% accuracy when parser gets half right."""
        tests_data = {
            "tests": [
                {"path": "assets/patent1.pdf", "abstract": "Correct abstract"},
                {"path": "assets/patent2.pdf", "abstract": "Another abstract"},
            ]
        }

        tests_yml = mock_tests_dir / "tests.yml"
        with open(tests_yml, "w") as f:
            yaml.dump(tests_data, f)

        def mock_parser(pdf_path: str) -> str:
            if "patent1" in pdf_path:
                return "Correct abstract"  # Exact match
            return "Wrong output"

        with patch("patent_test.evaluator.__file__", str(mock_tests_dir / "evaluator.py")):
            accuracy, avg_distance = evaluate(mock_parser)

        assert accuracy == 0.5

    def test_levenshtein_distance_calculation(self, mock_tests_dir):
        """Test that Levenshtein distance is calculated correctly."""
        tests_data = {
            "tests": [
                {"path": "assets/patent1.pdf", "abstract": "hello world"},
            ]
        }

        tests_yml = mock_tests_dir / "tests.yml"
        with open(tests_yml, "w") as f:
            yaml.dump(tests_data, f)

        def mock_parser(pdf_path: str) -> str:
            return "hello there"  # "world" -> "there" = different words

        with patch("patent_test.evaluator.__file__", str(mock_tests_dir / "evaluator.py")):
            accuracy, avg_distance = evaluate(mock_parser)

        # Normalized: "hello world" vs "hello there"
        expected_distance = _levenshtein("hello world", "hello there")
        assert accuracy == 0.0
        assert avg_distance == expected_distance

    def test_normalization_allows_match(self, mock_tests_dir):
        """Test that normalization allows matches with different punctuation/case."""
        tests_data = {
            "tests": [
                {"path": "assets/patent1.pdf", "abstract": "Hello, World!"},
            ]
        }

        tests_yml = mock_tests_dir / "tests.yml"
        with open(tests_yml, "w") as f:
            yaml.dump(tests_data, f)

        def mock_parser(pdf_path: str) -> str:
            return "hello world"  # No punctuation, lowercase

        with patch("patent_test.evaluator.__file__", str(mock_tests_dir / "evaluator.py")):
            accuracy, avg_distance = evaluate(mock_parser)

        assert accuracy == 1.0
        assert avg_distance == 0.0

    def test_empty_tests(self, mock_tests_dir):
        """Test handling of empty test suite."""
        tests_data = {"tests": []}

        tests_yml = mock_tests_dir / "tests.yml"
        with open(tests_yml, "w") as f:
            yaml.dump(tests_data, f)

        def mock_parser(pdf_path: str) -> str:
            return ""

        with patch("patent_test.evaluator.__file__", str(mock_tests_dir / "evaluator.py")):
            accuracy, avg_distance = evaluate(mock_parser)

        assert accuracy == 0.0
        assert avg_distance == 0.0

    def test_three_tests_one_correct(self, mock_tests_dir):
        """Test accuracy calculation with 1/3 correct."""
        tests_data = {
            "tests": [
                {"path": "assets/patent1.pdf", "abstract": "First abstract"},
                {"path": "assets/patent2.pdf", "abstract": "Second abstract"},
                {"path": "assets/patent3.pdf", "abstract": "Third abstract"},
            ]
        }

        tests_yml = mock_tests_dir / "tests.yml"
        with open(tests_yml, "w") as f:
            yaml.dump(tests_data, f)

        def mock_parser(pdf_path: str) -> str:
            if "patent2" in pdf_path:
                return "Second abstract"  # Only this one matches
            return "wrong"

        with patch("patent_test.evaluator.__file__", str(mock_tests_dir / "evaluator.py")):
            accuracy, avg_distance = evaluate(mock_parser)

        assert accuracy == pytest.approx(1 / 3)

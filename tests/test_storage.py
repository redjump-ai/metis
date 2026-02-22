"""Tests for storage module."""
import pytest
from datetime import datetime
from metis.storage import _clean_title, _sanitize_filename, format_frontmatter


class TestCleanTitle:
    """Tests for _clean_title function."""

    def test_strip_author_prefix_with_colon(self):
        """Test stripping author prefix with colon."""
        assert _clean_title("XinGPT on X: Agent大爆发") == "Agent大爆发"
        assert _clean_title("John on Twitter: Hello World") == "Hello World"

    def test_no_colon_returns_original(self):
        """Test that title without colon returns original."""
        assert _clean_title("Simple Title") == "Simple Title"

    def test_empty_after_colon_returns_original(self):
        """Test handling of empty content after colon."""
        assert _clean_title("Author:") == "Author:"

    def test_chinese_title_with_author(self):
        """Test Chinese title with author prefix."""
        assert _clean_title("张三 on 知乎: 如何学习Python") == "如何学习Python"


class TestSanitizeFilename:
    """Tests for _sanitize_filename function."""

    def test_removes_special_chars(self):
        """Test that special characters are removed."""
        result = _sanitize_filename("Test <file> name")
        assert "<" not in result
        assert ">" not in result

    def test_replaces_spaces_with_dash(self):
        """Test that spaces are replaced with dashes."""
        result = _sanitize_filename("Test File Name")
        assert " " not in result

    def test_strips_author_prefix(self):
        """Test that author prefix is stripped."""
        result = _sanitize_filename("Author on X: Title")
        assert "Author" not in result
        assert "Title" in result

    def test_truncates_long_titles(self):
        """Test that long titles are truncated."""
        long_title = "A" * 100
        result = _sanitize_filename(long_title)
        assert len(result) <= 80


class TestFormatFrontmatter:
    """Tests for format_frontmatter function."""

    def test_basic_frontmatter(self):
        """Test basic frontmatter generation."""
        result = format_frontmatter(
            title="Test Title",
            url="https://example.com",
            platform="twitter",
            created=datetime(2026, 1, 1, 12, 0, 0),
            status="pending",
        )
        assert "title: \"Test Title\"" in result
        assert "url: \"https://example.com\"" in result
        assert "platform: \"twitter\"" in result

    def test_escapes_quotes_in_title(self):
        """Test that quotes in title are escaped."""
        result = format_frontmatter(
            title='Title with "quotes"',
            url="https://example.com",
            platform="twitter",
            created=datetime.now(),
            status="pending",
        )
        assert '\\"' in result

    def test_strips_author_from_title(self):
        """Test that author prefix is stripped from frontmatter title."""
        result = format_frontmatter(
            title="Author on X: Real Title",
            url="https://example.com",
            platform="twitter",
            created=datetime.now(),
            status="pending",
        )
        assert "Real Title" in result
        assert "Author on X:" not in result

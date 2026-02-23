"""Tests for processors module - summarization and image processing."""
import pytest
from metis.processors import (
    sanitize_filename,
    extract_image_urls,
    summarize_text,
    ProcessedContent,
)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_removes_special_chars(self):
        """Test that special characters are removed."""
        result = sanitize_filename("Test <file> name")
        assert "<" not in result
        assert ">" not in result

    def test_truncates_long_names(self):
        """Test that long filenames are truncated."""
        long_name = "A" * 150
        result = sanitize_filename(long_name)
        assert len(result) <= 100

    def test_returns_untitled_for_empty(self):
        """Test that empty input returns 'untitled'."""
        result = sanitize_filename("")
        assert result == "untitled"


class TestExtractImageUrls:
    """Tests for extract_image_urls function."""

    def test_extracts_markdown_images(self):
        """Test extracting markdown image syntax."""
        markdown = "![Image](https://example.com/image.jpg)"
        urls = extract_image_urls(markdown)
        assert "https://example.com/image.jpg" in urls

    def test_extracts_html_images(self):
        """Test extracting HTML image syntax."""
        markdown = '<img src="https://example.com/image.png">'
        urls = extract_image_urls(markdown)
        assert "https://example.com/image.png" in urls

    def test_extracts_xiaohongshu_urls(self):
        """Test extracting Xiaohongshu image URLs."""
        markdown = "Check this: https://example.xiaohongshu.com/image.jpg"
        urls = extract_image_urls(markdown)
        assert "https://example.xiaohongshu.com/image.jpg" in urls

    def test_extracts_feishu_urls(self):
        """Test extracting Feishu image URLs."""
        markdown = "https://example.feishu.cn/image.png"
        urls = extract_image_urls(markdown)
        assert "https://example.feishu.cn/image.png" in urls

    def test_removes_duplicates(self):
        """Test that duplicate URLs are removed."""
        markdown = "![img](https://example.com/img.jpg)\n![img](https://example.com/img.jpg)"
        urls = extract_image_urls(markdown)
        assert len(urls) == 1


class TestSummarizeText:
    """Tests for summarize_text function."""

    def test_basic_summarization(self):
        """Test basic text summarization."""
        markdown = """# Article Title

This is the first paragraph with meaningful content about machine learning.

This is the second paragraph discussing artificial intelligence applications.

This is the third paragraph about deep learning techniques.
"""
        result = summarize_text(markdown, max_length=100)
        assert len(result) > 0
        assert len(result) <= 150  # Should include ellipsis

    def test_removes_code_blocks(self):
        """Test that code blocks are removed."""
        markdown = """# Title

Some text here.

```python
def hello():
    print("world")
```

More text.
"""
        result = summarize_text(markdown)
        assert "def hello" not in result

    def test_removes_inline_code(self):
        """Test that inline code is removed."""
        markdown = "# Title\n\nUse `print()` function."
        result = summarize_text(markdown)
        assert "print()" not in result

    def test_removes_image_references(self):
        """Test that image references are removed."""
        markdown = "# Title\n\n![image](https://example.com/img.jpg)"
        result = summarize_text(markdown)
        assert "example.com" not in result

    def test_keeps_link_text(self):
        """Test that link text is preserved."""
        markdown = "# Title\n\nCheck [this link](https://example.com) for more."
        result = summarize_text(markdown)
        assert "this link" in result

    def test_skips_short_paragraphs(self):
        """Test that short paragraphs are skipped."""
        markdown = """# Title

Short.

This is a meaningful paragraph with enough content to be considered for summarization.
"""
        result = summarize_text(markdown)
        assert "meaningful paragraph" in result

    def test_handles_empty_content(self):
        """Test handling of empty content."""
        result = summarize_text("")
        assert result == ""

    def test_handles_only_metadata(self):
        """Test handling of content with only metadata."""
        markdown = """---
title: Test
---

---

"""
        result = summarize_text(markdown)
        assert result == ""


class TestProcessedContent:
    """Tests for ProcessedContent dataclass."""

    def test_default_summary(self):
        """Test that summary defaults to empty string."""
        content = ProcessedContent(
            title="Test",
            markdown="Content",
            images=[],
            url="https://example.com",
            platform_name="test",
        )
        assert content.summary == ""

    def test_custom_summary(self):
        """Test custom summary value."""
        content = ProcessedContent(
            title="Test",
            markdown="Content",
            images=[],
            url="https://example.com",
            platform_name="test",
            summary="Custom summary",
        )
        assert content.summary == "Custom summary"

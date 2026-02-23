"""Markdown formatting utilities using mdformat and trafilatura."""
import re


def format_markdown(markdown: str) -> str:
    """Format markdown content to make it more readable.
    
    Uses mdformat for consistent styling and applies custom fixes
    for better Obsidian compatibility.
    
    Args:
        markdown: Raw markdown content
        
    Returns:
        Formatted markdown content
    """
    try:
        import mdformat
        from mdformat.plugins import GFM

        # Format with GFM (GitHub Flavored Markdown) support
        options = {"plugin": {"gfm": GFM()}}
        formatted = mdformat.text(markdown, options=options)
        return formatted
    except Exception:
        # Fallback to basic formatting if mdformat fails
        return _basic_format(markdown)


def _basic_format(markdown: str) -> str:
    """Basic markdown formatting as fallback."""
    lines = markdown.split("\n")
    formatted_lines = []
    
    for line in lines:
        # Fix multiple blank lines
        if line.strip() == "" and formatted_lines and formatted_lines[-1].strip() == "":
            continue
        formatted_lines.append(line)
    
    # Remove trailing whitespace
    formatted_lines = [line.rstrip() for line in formatted_lines]
    
    return "\n".join(formatted_lines)


def clean_markdown(markdown: str) -> str:
    """Clean and normalize markdown content.
    
    Removes unnecessary elements and normalizes formatting.
    
    Args:
        markdown: Raw markdown content
        
    Returns:
        Cleaned markdown content
    """
    # Remove multiple consecutive newlines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    
    # Remove trailing whitespace on lines
    lines = [line.rstrip() for line in markdown.split("\n")]
    markdown = "\n".join(lines)
    
    # Fix spacing around headers
    markdown = re.sub(r"\n(#+ )", r"\n\n\1", markdown)
    markdown = re.sub(r"(#+ .+)\n([^\n#])", r"\1\n\n\2", markdown)
    
    # Remove empty list items
    markdown = re.sub(r"^- \s*$\n", "", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^\d+\. \s*$\n", "", markdown, flags=re.MULTILINE)
    
    # Clean up code blocks
    markdown = re.sub(r"```\s*", "```", markdown)
    
    return markdown.strip()


def extract_with_trafilatura(html: str) -> str | None:
    """Extract clean markdown from HTML using trafilatura.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Extracted markdown content, or None if extraction fails
    """
    try:
        from trafilatura import extract
        
        result = extract(
            html,
            output_format="markdown",
            with_metadata=True,
            include_images=True,
            include_links=True,
        )
        return result
    except Exception:
        return None


def convert_html_to_markdown(html: str) -> str:
    """Convert HTML to clean markdown.
    
    Uses trafilatura first, falls back to basic conversion.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Markdown content
    """
    # Try trafilatura first
    markdown = extract_with_trafilatura(html)
    if markdown and len(markdown) > 100:
        return markdown
    
    # Fallback to basic conversion
    try:
        from markdown import markdown as md_convert
        
        # Basic HTML to markdown conversion
        html_clean = re.sub(r"<br\s*/?>", "\n", html)
        html_clean = re.sub(r"</?p[^>]*>", "\n\n", html_clean)
        html_clean = re.sub(r"</?div[^>]*>", "", html_clean)
        html_clean = re.sub(r"<h1[^>]*>(.+?)</h1>", r"# \1\n", html_clean)
        html_clean = re.sub(r"<h2[^>]*>(.+?)</h2>", r"## \1\n", html_clean)
        html_clean = re.sub(r"<h3[^>]*>(.+?)</h3>", r"### \1\n", html_clean)
        html_clean = re.sub(r"<h4[^>]*>(.+?)</h4>", r"#### \1\n", html_clean)
        html_clean = re.sub(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.+?)</a>", r"[\2](\1)", html_clean)
        html_clean = re.sub(r"<img[^>]*src=\"([^\"]+)\"[^>]*alt=\"([^\"]+)\"[^>]*>", r"![\2](\1)", html_clean)
        html_clean = re.sub(r"<img[^>]*src=\"([^\"]+)\"[^>]*>", r"![](\1)", html_clean)
        html_clean = re.sub(r"<strong[^>]*>(.+?)</strong>", r"**\1**", html_clean)
        html_clean = re.sub(r"<b[^>]*>(.+?)</b>", r"**\1**", html_clean)
        html_clean = re.sub(r"<em[^>]*>(.+?)</em>", r"*\1*", html_clean)
        html_clean = re.sub(r"<i[^>]*>(.+?)</i>", r"*\1*", html_clean)
        html_clean = re.sub(r"<code[^>]*>(.+?)</code>", r"`\1`", html_clean)
        html_clean = re.sub(r"<li[^>]*>(.+?)</li>", r"- \1\n", html_clean)
        html_clean = re.sub(r"<ul[^>]*>|</ul>", "", html_clean)
        html_clean = re.sub(r"<ol[^>]*>|</ol>", "", html_clean)
        html_clean = re.sub(r"<[^>]+>", "", html_clean)
        html_clean = re.sub(r"&nbsp;", " ", html_clean)
        html_clean = re.sub(r"&amp;", "&", html_clean)
        html_clean = re.sub(r"&lt;", "<", html_clean)
        html_clean = re.sub(r"&gt;", ">", html_clean)
        
        return html_clean.strip()
    except Exception:
        return html

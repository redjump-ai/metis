"""Obsidian storage and sync module."""
import re
from datetime import datetime
from pathlib import Path

from metis.config import settings
from metis.processors import ProcessedContent


def format_frontmatter(
    title: str,
    url: str,
    platform: str,
    created: datetime,
    status: str = "pending",
    tags: list[str] | None = None,
) -> str:
    tags_str = ", ".join(f'"{t}"' for t in (tags or []))
    # Escape quotes in title for valid YAML
    escaped_title = title.replace('"', '\\"')
    return f"""---
title: "{escaped_title}"
url: "{url}"
platform: "{platform}"
created: {created.isoformat()}
status: "{status}"
tags: [{tags_str}]
---

"""


def _sanitize_filename(name: str) -> str:
    # If there's a colon, keep only what comes after it (strip author prefix)
    if ':' in name:
        parts = name.split(':', 1)
        if parts[1].strip():
            name = parts[1].strip()
    # Remove special characters
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = name.replace(" ", "-")
    # Keep only alphanumeric, Chinese, and basic punctuation
    name = re.sub(r'[^\w\u4e00-\u9fff\-_]', "", name)
    return name[:80] or "untitled"


def get_content_path(url: str) -> Path | None:
    inbox_path = settings.obsidian_vault_path / settings.inbox_path
    if not inbox_path.exists():
        return None

    for md_file in inbox_path.glob("*.md"):
        if url in md_file.read_text():
            return md_file

    return None


def _update_frontmatter_status(file_path: Path, status: str):
    """Update status in frontmatter of existing file, preserving body."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return
    
    if not content.startswith("---"):
        return
    
    # Find frontmatter boundaries - match from start to the second ---
    # Frontmatter ends with "---" followed by newline
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False
    body_start = 0
    
    for i, line in enumerate(lines):
        if i == 0 and line == '---':
            in_frontmatter = True
            frontmatter_lines.append(line)
        elif in_frontmatter and line == '---':
            frontmatter_lines.append(line)
            body_start = i + 1
            break
        elif in_frontmatter:
            frontmatter_lines.append(line)
    
    if body_start == 0:
        return
    
    # Update status line
    new_frontmatter_lines = []
    for line in frontmatter_lines:
        if line.startswith('status:'):
            new_frontmatter_lines.append(f'status: "{status}"')
        else:
            new_frontmatter_lines.append(line)
    
    # Rebuild file
    new_content = '\n'.join(new_frontmatter_lines) + '\n' + '\n'.join(lines[body_start:])
    file_path.write_text(new_content, encoding="utf-8")


def save_to_obsidian(content: ProcessedContent, status: str = "pending", use_inbox: bool = True) -> Path:
    vault_path = settings.obsidian_vault_path
    vault_path.mkdir(parents=True, exist_ok=True)

    if use_inbox:
        # Save as individual files in inbox_path (not folders)
        base_path = vault_path / settings.inbox_path
    else:
        base_path = vault_path
    
    base_path.mkdir(parents=True, exist_ok=True)

    # Check if file already exists for this URL (by searching in content)
    existing_path = get_content_path(content.url)
    if existing_path and existing_path.exists():
        # Update status in existing file's frontmatter
        _update_frontmatter_status(existing_path, status)
        return existing_path
    
    # Generate filename from title only (no date, no hash suffix)
    safe_title = _sanitize_filename(content.title)
    filename = f"{safe_title[:50]}.md"
    file_path = base_path / filename

    frontmatter = format_frontmatter(
        title=content.title,
        url=content.url,
        platform=content.platform_name,
        created=datetime.now(),
        status=status,
        tags=[content.platform_name, "metis"],
    )

    file_path.write_text(frontmatter + content.markdown, encoding="utf-8")

    return file_path


def read_url_inbox() -> list[str]:
    """Read URLs from the inbox markdown file."""
    inbox_file = settings.obsidian_vault_path / settings.url_inbox_md
    
    if not inbox_file.exists():
        return []
    
    content = inbox_file.read_text(encoding="utf-8")
    
    # Extract URLs from markdown links or plain URLs
    urls = []
    
    # Match markdown links: [text](url) - capture only the URL
    urls.extend(re.findall(r'\[[^\]]+\]\((https?://[^\)]+)\)', content))
    
    # Match plain URLs
    urls.extend(re.findall(r'https?://[^\s\)>\]]+', content))
    
    # Return unique URLs
    return list(set([url for url in urls if url]))

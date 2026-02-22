"""URL status tracking - reading from inbox files."""
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from metis.config import settings


def _read_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}
    
    # Find the closing ---
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    frontmatter_text = match.group(1)
    result = {}
    
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Handle YAML arrays: ["a", "b"] or ['a', 'b']
            if value.startswith('[') and value.endswith(']'):
                # Parse as YAML array
                inner = value[1:-1]
                items = []
                for item in inner.split(','):
                    item = item.strip().strip('"').strip("'")
                    if item:
                        items.append(item)
                result[key] = items
            else:
                value = value.strip('"').strip("'")
                result[key] = value
    
    return result


def _write_frontmatter_update(file_path: Path, updates: dict):
    """Update frontmatter of an existing file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return
    
    if not content.startswith("---"):
        return
    
    # Find frontmatter boundaries
    match = re.match(r'^(---\s*\n.*?\n---)', content, re.DOTALL)
    if not match:
        return
    
    # Parse existing frontmatter
    existing = _read_frontmatter(content)
    existing.update(updates)
    
    # Rebuild frontmatter
    lines = ["---"]
    for key, value in existing.items():
        if value is None:
            value = ""
        if isinstance(value, bool):
            value = str(value).lower()
        elif isinstance(value, list):
            # Handle arrays: ["a", "b"]
            items = ', '.join(f'"{item}"' for item in value)
            value = f"[{items}]"
        elif isinstance(value, str):
            value = f'"{value}"'
        else:
            value = f'"{value}"'
        lines.append(f"{key}: {value}")
    lines.append("---")
    new_frontmatter = "\n".join(lines)
    
    # Replace frontmatter, keep body
    body_start = match.end()
    body = content[body_start:]
    
    new_content = new_frontmatter + body
    file_path.write_text(new_content, encoding="utf-8")


class URLDatabase:
    """URL status tracking - reads from inbox files."""
    
    def _get_inbox_path(self) -> Path:
        """Get the inbox path."""
        return settings.obsidian_vault_path / settings.inbox_path
    
    def _find_url_file(self, url: str) -> Optional[Path]:
        """Find the inbox file that contains this URL."""
        inbox_path = self._get_inbox_path()
        if not inbox_path.exists():
            return None
        
        for md_file in inbox_path.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                if url in content:
                    return md_file
            except Exception:
                continue
        
        return None
    
    def add_url(self, url: str, title: str = "", platform: str = "unknown") -> int:
        """Add a URL entry (no-op, data is in inbox files)."""
        return 1
    
    def update_status(self, url: str, status: str, folder_path: Optional[str] = None):
        """Update status in the inbox file's frontmatter."""
        file_path = self._find_url_file(url)
        if not file_path:
            return
        
        now = datetime.now().isoformat()
        
        data = {"status": status}
        
        if status == "extracted":
            data["extracted_at"] = now
            if folder_path:
                data["file"] = folder_path
        elif status == "read":
            data["read_at"] = now
        elif status == "valuable":
            data["valuable_at"] = now
        elif status == "archived":
            data["archived_at"] = now
        elif status == "failed":
            data["failed_at"] = now
        
        _write_frontmatter_update(file_path, data)
    
    def get_url(self, url: str) -> Optional[dict]:
        """Get URL data from inbox file."""
        file_path = self._find_url_file(url)
        if not file_path:
            return None
        
        try:
            content = file_path.read_text(encoding="utf-8")
            data = _read_frontmatter(content)
            if data:
                data["file_path"] = str(file_path)
                return data
        except Exception:
            pass
        
        return None
    
    def get_all_urls(self, status: Optional[str] = None) -> list[dict]:
        """Get all URLs from inbox files."""
        inbox_path = self._get_inbox_path()
        
        if not inbox_path.exists():
            return []
        
        urls = []
        
        for md_file in inbox_path.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                data = _read_frontmatter(content)
                
                if data and data.get("url"):  # Only files with URL in frontmatter
                    data["file_path"] = str(md_file)
                    
                    if status is None or data.get("status") == status:
                        urls.append(data)
            except Exception:
                continue
        
        # Sort by created date, newest first
        urls.sort(key=lambda x: x.get("created", ""), reverse=True)
        
        return urls
    
    def delete_url(self, url: str):
        """Delete URL entry (no-op, data is in inbox files)."""
        pass
    
    def mark_english(self, url: str):
        """Mark as English in inbox file."""
        file_path = self._find_url_file(url)
        if file_path:
            _write_frontmatter_update(file_path, {"is_english": True})
    
    def mark_translated(self, url: str):
        """Mark as translated in inbox file."""
        file_path = self._find_url_file(url)
        if file_path:
            _write_frontmatter_update(file_path, {"has_translation": True})
    
    def add_note(self, url: str, note: str):
        """Add note to inbox file."""
        file_path = self._find_url_file(url)
        if file_path:
            _write_frontmatter_update(file_path, {"notes": note})


def ensure_base_file():
    """Create/update the Obsidian Bases .base file for the inbox folder."""
    inbox_path = settings.obsidian_vault_path / settings.inbox_path
    base_file_path = inbox_path.with_suffix('.base')
    
    # Get all URLs from inbox files
    db = URLDatabase()
    urls = db.get_all_urls()
    
    # Build base file content (YAML format for Obsidian Bases)
    lines = [
        "title: Inbox URLs",
        "type: dynamic",
        "sources:",
    ]
    
    for url_data in urls:
        title = url_data.get("title", "Untitled")
        url = url_data.get("url", "")
        status = url_data.get("status", "pending")
        platform = url_data.get("platform", "unknown")
        
        lines.append(f"  - title: \"{title}\"")
        lines.append(f"    url: \"{url}\"")
        lines.append(f"    status: \"{status}\"")
        lines.append(f"    platform: \"{platform}\"")
        lines.append("")
    
    base_file_path.write_text("\n".join(lines), encoding="utf-8")


url_db = URLDatabase()

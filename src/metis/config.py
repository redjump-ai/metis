"""Metis configuration module."""

import os
from pathlib import Path
from typing import Optional

# Try to load .env file
try:
    from dotenv import load_dotenv
    # Load .env from project root (where pyproject.toml is)
    project_root = Path(__file__).parent.parent.parent
    load_dotenv(dotenv_path=project_root / ".env", override=False)
except ImportError:
    pass


class Settings:
    base_path: Path = Path("./data")  # Base path for metis data (URL database, etc.)
    firecrawl_api_key: Optional[str] = None
    obsidian_vault_path: Path = Path("./obsidian-vault")
    url_inbox_md: str = "URL_INBOX.md"  # Input: markdown file with URLs to process
    inbox_path: str = "inbox"  # Output: folder for processed content (as files)
    media_folder: Path = Path("./data/media")
    archive_folder: Path = Path("./data/archive")
    translation_target_lang: str = "zh"
    fetch_timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    playwright_state_path: Path = Path("./data/playwright_state.json")
    wechat_auth_path: Path = Path("./data/wechat_auth.json")

    def __init__(self):
        # Load vault_path first (needed for relative base_path)
        vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
        if vault_path:
            # Handle escaped spaces from .env
            vault_path = vault_path.replace('\\ ', ' ')
            self.obsidian_vault_path = Path(vault_path)
        
        # Load base_path - support relative paths (relative to vault)
        base_path = os.getenv("BASE_PATH")
        if base_path:
            base_path = base_path.replace('\\ ', ' ')
            base_path = Path(base_path)
            # If relative, resolve relative to vault
            if not base_path.is_absolute():
                base_path = self.obsidian_vault_path / base_path
            self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        
        url_inbox_md = os.getenv("URL_INBOX_MD")
        if url_inbox_md:
            self.url_inbox_md = url_inbox_md
        
        inbox_path = os.getenv("INBOX_PATH")
        if inbox_path:
            self.inbox_path = inbox_path
        
        media_folder = os.getenv("MEDIA_FOLDER")
        if media_folder:
            self.media_folder = Path(media_folder)
        
        archive_folder = os.getenv("ARCHIVE_FOLDER")
        if archive_folder:
            self.archive_folder = Path(archive_folder)
        
        target_lang = os.getenv("TRANSLATION_TARGET_LANG")
        if target_lang:
            self.translation_target_lang = target_lang
        
        timeout = os.getenv("FETCH_TIMEOUT")
        if timeout:
            self.fetch_timeout = int(timeout)
        
        user_agent = os.getenv("USER_AGENT")
        if user_agent:
            self.user_agent = user_agent
        
        pw_state = os.getenv("PLAYWRIGHT_STATE_PATH")
        if pw_state:
            self.playwright_state_path = Path(pw_state)
        
        self.obsidian_vault_path.mkdir(parents=True, exist_ok=True)
        self.media_folder.mkdir(parents=True, exist_ok=True)
        self.archive_folder.mkdir(parents=True, exist_ok=True)
        
        # Create inbox path folder
        inbox_full_path = self.obsidian_vault_path / self.inbox_path
        inbox_full_path.mkdir(parents=True, exist_ok=True)


settings = Settings()

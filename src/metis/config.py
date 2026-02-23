import json
from typing import Any, Dict


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

# Load model configuration from JSON
_model_config: Dict[str, Any] = {}


def load_model_config() -> Dict[str, Any]:
    """Load model configuration from JSON file."""
    global _model_config
    if not _model_config:
        config_path = project_root / "config" / "models.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                _model_config = json.load(f)
    return _model_config


def get_model_config(provider: str, model: Optional[str] = None) -> Dict[str, Any]:
    """Get model configuration for a specific provider and model.

    Args:
        provider: LLM provider (openai, anthropic, ollama)
        model: Model name (optional, uses default if not specified)

    Returns:
        Dict with model configuration (name, temperature, max_tokens)
    """
    config = load_model_config()
    providers = config.get("providers", {})

    if provider not in providers:
        # Return defaults if provider not in config
        return {"name": model or "gpt-4o-mini", "temperature": 0.7, "max_tokens": 500}

    provider_config = providers[provider]

    # Use default model if not specified
    if not model:
        model = provider_config.get("default_model", "gpt-4o-mini")

    models = provider_config.get("models", {})
    model_config = models.get(model, {})

    # Return model config or defaults
    return {
        "name": model_config.get("name", model),
        "temperature": model_config.get("temperature", 0.7),
        "max_tokens": model_config.get("max_tokens", 500),
    }


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
    
    # LLM Configuration
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    summarization_prompt: str = """请为以下文章生成一个简洁的中文摘要,不超过200字,概括文章的主要内容和核心观点:

{{content}}

摘要:"""

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
        
        # LLM Configuration
        llm_provider = os.getenv("LLM_PROVIDER")
        if llm_provider:
            self.llm_provider = llm_provider
        
        llm_model = os.getenv("LLM_MODEL")
        if llm_model:
            self.llm_model = llm_model
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_api_key = openai_key
        
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.anthropic_api_key = anthropic_key
        
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        if ollama_url:
            self.ollama_base_url = ollama_url
        
        # Load summarization prompt from JSON config first, then allow .env override
        model_config = load_model_config()
        json_prompt = model_config.get("summarization_prompt")
        if json_prompt:
            self.summarization_prompt = json_prompt

        prompt = os.getenv("SUMMARIZATION_PROMPT")
        if prompt:
            self.summarization_prompt = prompt
        
        self.obsidian_vault_path.mkdir(parents=True, exist_ok=True)
        self.media_folder.mkdir(parents=True, exist_ok=True)
        self.archive_folder.mkdir(parents=True, exist_ok=True)
        
        # Create inbox path folder
        inbox_full_path = self.obsidian_vault_path / self.inbox_path
        inbox_full_path.mkdir(parents=True, exist_ok=True)


settings = Settings()

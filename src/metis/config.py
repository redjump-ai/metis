"""Metis configuration module.

Supports multiple configuration sources with priority:
env vars > .env > YAML/TOML config files

Configuration files (in order of priority, later overrides earlier):
- config.yaml or config.toml (project root)
- .env file (project root, loaded by python-dotenv)

Environment variables always take highest priority and can override any config file setting.
"""

import json
from pathlib import Path
from typing import Any

# Define project_root at module level (needed for Settings class)
project_root = Path(__file__).parent.parent.parent

try:
    import tomllib
except ImportError:
    import tomli as tomllib
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Try to load .env file
try:
    from dotenv import load_dotenv

    # Load .env from project root (where pyproject.toml is)
    project_root = Path(__file__).parent.parent.parent
    load_dotenv(dotenv_path=project_root / ".env", override=False)
except ImportError:
    pass


def load_yaml_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        return {}
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_toml_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from TOML file."""
    if not config_path.exists():
        return {}
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def load_json_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from JSON file."""
    if not config_path.exists():
        return {}
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def find_config_file() -> Path | None:
    """Find the first existing config file in project root."""
    project_root = Path(__file__).parent.parent.parent
    config_files = ["config.yaml", "config.yml", "config.toml"]
    for filename in config_files:
        config_path = project_root / filename
        if config_path.exists():
            return config_path
    return None


# Load model configuration from merged config.yaml
def load_model_config() -> dict[str, Any]:
    """Load model configuration from config.yaml."""
    config_file = find_config_file()
    if config_file and config_file.suffix in [".yaml", ".yml"]:
        full_config = load_yaml_config(config_file)
        return full_config.get("models", {})
    return {}


def get_model_config(provider: str, model: str | None = None) -> dict[str, Any]:
    """Get model configuration for a specific provider and model.

    Args:
        provider: LLM provider (openai, anthropic, ollama, zhipu)
        model: Model name (optional, uses default if not specified)

    Returns:
        Dict with model configuration (name, temperature, max_tokens, base_url)
    """
    config = load_model_config()
    # config.yaml 'models' section directly contains provider configs
    providers = config

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
    result = {
        "name": model_config.get("name", model),
        "temperature": model_config.get("temperature", 0.7),
        "max_tokens": model_config.get("max_tokens", 500),
    }
    # Add base_url if specified for this provider
    if provider_config.get("base_url"):
        result["base_url"] = provider_config["base_url"]
    return result


class LLMProviderSettings(BaseSettings):
    """LLM Provider configuration with environment variable support."""

    provider: str = Field(default="openai", description="LLM provider name")
    model: str = Field(default="gpt-4o-mini", description="Model name")
    api_key: str | None = Field(default=None, description="Provider API key")
    base_url: str | None = Field(default=None, description="Custom API base URL")

    model_config = SettingsConfigDict(
        env_prefix="",
        extra="allow",
    )


class Settings(BaseSettings):
    """Metis application settings.

    Supports configuration from multiple sources:
    - config.yaml / config.yml / config.toml (project root)
    - .env file (project root)
    - Environment variables (highest priority)

    Environment variables take precedence over all file-based configuration.
    For nested settings, use double underscore separator in env var names.
    Example: FIRECRAWL_API_KEY, LLM_PROVIDER__MODEL, etc.
    """

    # Core Paths
    base_path: Path = Field(
        default=Path("./data"),
        description="Base path for metis data (URL database, etc.)",
    )
    obsidian_vault_path: Path = Field(
        default=Path("./obsidian-vault"),
        description="Path to Obsidian vault",
    )
    url_inbox_md: str = Field(
        default="URL_INBOX.md",
        description="Input: markdown file with URLs to process",
    )
    inbox_path: str = Field(
        default="inbox",
        description="Output: folder for processed content",
    )
    media_folder: Path = Field(
        default=Path("./data/media"),
        description="Folder for downloaded media files",
    )
    archive_folder: Path = Field(
        default=Path("./data/archive"),
        description="Folder for archived content",
    )

    # Fetching
    translation_target_lang: str = Field(
        default="zh",
        description="Target language for translation",
    )
    fetch_timeout: int = Field(
        default=30,
        description="Fetch timeout in seconds",
    )
    user_agent: str = Field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        description="User agent for HTTP requests",
    )
    playwright_state_path: Path = Field(
        default=Path("./data/playwright_state.json"),
        description="Path to Playwright state file",
    )
    wechat_auth_path: Path = Field(
        default=Path("./data/wechat_auth.json"),
        description="Path to WeChat auth file",
    )

    # API Keys
    firecrawl_api_key: str | None = Field(
        default=None,
        description="Firecrawl API key",
    )

    # LLM Configuration
    llm_provider: str = Field(
        default="openai",
        description="LLM provider (openai, anthropic, ollama, zhipu)",
    )
    llm_model: str = Field(
        default="gpt-4o-mini",
        description="Default LLM model",
    )
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key",
    )
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key",
    )
    zhipu_api_key: str | None = Field(
        default=None,
        description="Zhipu API key",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL",
    )

    # Prompts
    summarization_prompt: str = Field(
        default="请为以下文章生成一个简洁的中文摘要,不超过200字,概括文章的主要内容和核心观点:\n\n{{content}}\n\n摘要:",
        description="Summarization prompt template",
    )

    model_config = SettingsConfigDict(
        env_file=(project_root / ".env"),
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="allow",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Post-initialization processing

        # Handle escaped spaces from .env
        vault_path = str(self.obsidian_vault_path)
        if vault_path and "\\ " in vault_path:
            vault_path = vault_path.replace('\\ ', ' ')
            self.obsidian_vault_path = Path(vault_path)

        base_path = str(self.base_path)
        if base_path and "\\ " in base_path:
            base_path = base_path.replace('\\ ', ' ')
            base_path = Path(base_path)
            # If relative, resolve relative to vault
            if not base_path.is_absolute():
                base_path = self.obsidian_vault_path / base_path
            self.base_path = base_path

        # Load summarization prompt from config.yaml first
        config_file = find_config_file()
        if config_file and config_file.suffix in [".yaml", ".yml"]:
            full_config = load_yaml_config(config_file)
            yaml_prompt = full_config.get("summarization_prompt")
            if yaml_prompt and self.summarization_prompt == Settings.model_fields["summarization_prompt"].default:
                self.summarization_prompt = yaml_prompt

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Create required directories if they don't exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.obsidian_vault_path.mkdir(parents=True, exist_ok=True)
        self.media_folder.mkdir(parents=True, exist_ok=True)
        self.archive_folder.mkdir(parents=True, exist_ok=True)

        # Create inbox path folder
        inbox_full_path = self.obsidian_vault_path / self.inbox_path
        inbox_full_path.mkdir(parents=True, exist_ok=True)

    def get_provider_config(self) -> LLMProviderSettings:
        """Get the current LLM provider configuration.

        Returns:
            LLMProviderSettings with current provider, model, and API key
        """
        api_key = None
        base_url = None

        # Get API key based on provider
        if self.llm_provider == "openai":
            api_key = self.openai_api_key
        elif self.llm_provider == "anthropic":
            api_key = self.anthropic_api_key
        elif self.llm_provider == "zhipu":
            api_key = self.zhipu_api_key
        elif self.llm_provider == "ollama":
            base_url = self.ollama_base_url

        # Try to get additional config from models.json
        model_config = get_model_config(self.llm_provider, self.llm_model)
        if "base_url" in model_config:
            base_url = model_config["base_url"]

        return LLMProviderSettings(
            provider=self.llm_provider,
            model=model_config.get("name", self.llm_model),
            api_key=api_key,
            base_url=base_url,
        )

    @classmethod
    def from_file(cls, config_path: Path | None = None) -> "Settings":
        """Create Settings from a config file.

        Args:
            config_path: Path to config file (YAML/TOML). If None, auto-detects.

        Returns:
            Settings instance with merged configuration
        """
        if config_path is None:
            config_path = find_config_file()

        if config_path is None:
            return cls()

        # Load file config
        if config_path.suffix in [".yaml", ".yml"]:
            file_config = load_yaml_config(config_path)
        elif config_path.suffix == ".toml":
            file_config = load_toml_config(config_path)
        else:
            file_config = {}

        # Merge with environment variables (pydantic handles this via BaseSettings)
        return cls(**file_config)


# Singleton instance - auto-load from config.yaml
settings = Settings.from_file()

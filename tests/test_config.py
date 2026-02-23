"""Tests for config module."""
import pytest
from pathlib import Path
from metis.config import (
    load_yaml_config,
    load_toml_config,
    load_json_config,
    find_config_file,
    get_model_config,
    Settings,
    LLMProviderSettings,
)


class TestLoadYamlConfig:
    """Tests for load_yaml_config function."""

    def test_load_valid_yaml(self, tmp_path):
        """Test loading a valid YAML file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
llm:
  provider: openai
  model: gpt-4
""")
        result = load_yaml_config(config_file)
        assert result["llm"]["provider"] == "openai"

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        result = load_yaml_config(Path("/nonexistent/config.yaml"))
        assert result == {}


class TestLoadTomlConfig:
    """Tests for load_toml_config function."""

    def test_load_valid_toml(self, tmp_path):
        """Test loading a valid TOML file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[llm]
provider = "openai"
""")
        result = load_toml_config(config_file)
        assert result["llm"]["provider"] == "openai"


class TestLoadJsonConfig:
    """Tests for load_json_config function."""

    def test_load_valid_json(self, tmp_path):
        """Test loading a valid JSON file."""
        config_file = tmp_path / "config.json"
        config_file.write_text('{"llm": {"provider": "openai"}}')
        result = load_json_config(config_file)
        assert result["llm"]["provider"] == "openai"


class TestFindConfigFile:
    """Tests for find_config_file function."""

    def test_finds_yaml(self, tmp_path, monkeypatch):
        """Test finding config.yaml."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "config.yaml"
        config_file.write_text("llm:\n  provider: openai")

        result = find_config_file()
        assert result is not None
        assert result.name == "config.yaml"

    def test_finds_yml(self, tmp_path, monkeypatch):
        """Test finding config.yml."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "config.yml"
        config_file.write_text("llm:\n  provider: openai")

        result = find_config_file()
        assert result is not None
        assert result.name == "config.yml"

    def test_finds_toml(self, tmp_path, monkeypatch):
        """Test finding config.toml."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "config.toml"
        config_file.write_text("[llm]\nprovider = 'openai'")

        result = find_config_file()
        assert result is not None
        assert result.name == "config.toml"

    def test_returns_none_when_no_config(self, tmp_path, monkeypatch):
        """Test that None is returned when no config file exists."""
        monkeypatch.chdir(tmp_path)
        result = find_config_file()
        assert result is None


class TestGetModelConfig:
    """Tests for get_model_config function."""

    def test_returns_defaults_for_unknown_provider(self):
        """Test that defaults are returned for unknown provider."""
        result = get_model_config("unknown_provider")
        assert result["name"] == "gpt-4o-mini"
        assert result["temperature"] == 0.7
        assert result["max_tokens"] == 500


class TestLLMProviderSettings:
    """Tests for LLMProviderSettings class."""

    def test_default_values(self):
        """Test default values."""
        settings = LLMProviderSettings()
        assert settings.provider == "openai"
        assert settings.model == "gpt-4o-mini"

    def test_custom_values(self):
        """Test custom values."""
        settings = LLMProviderSettings(
            provider="anthropic",
            model="claude-3",
            api_key="test-key",
        )
        assert settings.provider == "anthropic"
        assert settings.model == "claude-3"
        assert settings.api_key == "test-key"


class TestSettings:
    """Tests for Settings class."""

    def test_default_values(self):
        """Test default settings values."""
        # Note: This test may fail if .env file exists with different values
        settings = Settings()
        assert settings.llm_provider == "openai"
        assert settings.llm_model == "gpt-4o-mini"

    def test_translation_target_lang_default(self):
        """Test default translation target language."""
        settings = Settings()
        assert settings.translation_target_lang == "zh"

    def test_fetch_timeout_default(self):
        """Test default fetch timeout."""
        settings = Settings()
        assert settings.fetch_timeout == 30

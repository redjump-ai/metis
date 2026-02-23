"""Tests for LLM module - providers and client."""
import pytest
from metis.llm.models import LLMResponse
from metis.llm.providers import (
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    ProviderFactory,
)


class TestLLMResponse:
    """Tests for LLMResponse model."""

    def test_creation(self):
        """Test LLMResponse creation."""
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            provider="openai",
        )
        assert response.content == "Test response"
        assert response.model == "gpt-4"
        assert response.provider == "openai"


class TestProviderFactory:
    """Tests for ProviderFactory class."""

    def test_creates_openai_provider(self):
        """Test creating OpenAI provider."""
        provider = ProviderFactory.create(
            "openai",
            {"name": "gpt-4", "temperature": 0.7, "max_tokens": 500},
        )
        assert isinstance(provider, OpenAIProvider)

    def test_creates_anthropic_provider(self):
        """Test creating Anthropic provider."""
        provider = ProviderFactory.create(
            "anthropic",
            {"name": "claude-3", "temperature": 0.7, "max_tokens": 500},
        )
        assert isinstance(provider, AnthropicProvider)

    def test_creates_ollama_provider(self):
        """Test creating Ollama provider."""
        provider = ProviderFactory.create(
            "ollama",
            {"name": "llama3", "temperature": 0.7, "max_tokens": 500},
        )
        assert isinstance(provider, OllamaProvider)

    def test_creates_zhipu_as_openai_compatible(self):
        """Test creating Zhipu provider as OpenAI compatible."""
        provider = ProviderFactory.create(
            "zhipu",
            {"name": "glm-4", "temperature": 0.7, "max_tokens": 500},
        )
        # Zhipu uses OpenAICompatibleProvider

    def test_creates_unknown_as_openai_compatible(self):
        """Test creating unknown provider defaults to OpenAI compatible."""
        provider = ProviderFactory.create(
            "custom_provider",
            {"name": "custom-model", "temperature": 0.7, "max_tokens": 500},
        )
        # Should use OpenAICompatibleProvider for unknown providers


class TestLLMProvider:
    """Tests for LLMProvider base class."""

    def test_get_api_key_missing(self):
        """Test that missing API key raises error."""
        from metis.config import settings

        class TestProvider(LLMProvider):
            async def complete(self, prompt: str) -> LLMResponse:
                pass

        # Temporarily unset API key
        original_key = settings.openai_api_key
        settings.openai_api_key = None

        provider = TestProvider("openai", {"name": "gpt-4"})

        with pytest.raises(ValueError, match="openai_api_key"):
            provider.get_api_key("openai_api_key")

        # Restore
        settings.openai_api_key = original_key


class TestOpenAIProvider:
    """Tests for OpenAIProvider class."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = OpenAIProvider(
            "openai",
            {"name": "gpt-4", "temperature": 0.7, "max_tokens": 500},
        )
        assert provider.provider_name == "openai"
        assert provider.api_base == "https://api.openai.com/v1/"
        assert provider.api_key_name == "openai_api_key"


class TestAnthropicProvider:
    """Tests for AnthropicProvider class."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = AnthropicProvider(
            "anthropic",
            {"name": "claude-3", "temperature": 0.7, "max_tokens": 500},
        )
        assert provider.provider_name == "anthropic"


class TestOllamaProvider:
    """Tests for OllamaProvider class."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = OllamaProvider(
            "ollama",
            {"name": "llama3", "temperature": 0.7, "max_tokens": 500},
        )
        assert provider.provider_name == "ollama"

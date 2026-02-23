"""LLM client for article summarization."""
from typing import Optional

from metis.config import get_model_config, settings
from metis.llm.models import LLMResponse
from metis.llm.providers import ProviderFactory


class LLMClient:
    """Multi-provider LLM client (OpenAI, Anthropic, Ollama)."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ):
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model
        # Load model config from JSON
        self.model_config = get_model_config(self.provider, self.model)
        # Create provider instance
        self.provider_instance = ProviderFactory.create(self.provider, self.model_config)

    async def summarize(self, content: str, prompt: str | None = None) -> LLMResponse:
        """Generate summary using LLM."""
        prompt_template = prompt or settings.summarization_prompt
        # Reserve ~1000 chars for prompt template + response
        max_content_len = 6000
        # Truncate content to fit within context window
        truncated_content = content[:max_content_len] if len(content) > max_content_len else content
        user_prompt = prompt_template.replace("{{content}}", truncated_content)

        # Use provider instance for completion
        return await self.provider_instance.complete(user_prompt)


# Singleton instance
llm_client = LLMClient()

"""LLM provider abstractions and implementations."""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from metis.config import settings
from metis.llm.models import LLMResponse


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, provider_name: str, model_config: Dict):
        self.provider_name = provider_name
        self.model_config = model_config
    
    @abstractmethod
    async def complete(self, prompt: str) -> LLMResponse:
        """Generate completion for given prompt."""
        pass
    
    def get_api_key(self, key_name: str) -> str:
        """Get API key from settings."""
        api_key = getattr(settings, key_name, None)
        if not api_key:
            raise ValueError(f"{key_name.upper()} not configured")
        return api_key


class OpenAICompatibleProvider(LLMProvider):
    """Base class for providers compatible with OpenAI API format."""
    
    def __init__(self, provider_name: str, model_config: Dict):
        super().__init__(provider_name, model_config)
        # Default API endpoint for OpenAI compatible providers
        self.api_base = model_config.get("base_url", "https://api.openai.com/v1/")
        self.api_key_name = f"{provider_name}_api_key"
    
    async def complete(self, prompt: str) -> LLMResponse:
        """Call OpenAI compatible API."""
        import httpx
        
        # Get API key from settings
        api_key = self.get_api_key(self.api_key_name)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model_config["name"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.model_config["max_tokens"],
            "temperature": self.model_config["temperature"],
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.api_base}chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=self.model_config["name"],
                provider=self.provider_name,
            )


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, provider_name: str, model_config: Dict):
        super().__init__(provider_name, model_config)
        # Override API base for OpenAI
        self.api_base = "https://api.openai.com/v1/"
        self.api_key_name = "openai_api_key"


class AnthropicProvider(LLMProvider):
    """Anthropic provider implementation."""
    
    async def complete(self, prompt: str) -> LLMResponse:
        """Call Anthropic API."""
        import httpx
        
        api_key = self.get_api_key("anthropic_api_key")
        
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        
        payload = {
            "model": self.model_config["name"],
            "max_tokens": self.model_config["max_tokens"],
            "messages": [{"role": "user", "content": prompt}],
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["content"][0]["text"],
                model=self.model_config["name"],
                provider=self.provider_name,
            )


class OllamaProvider(LLMProvider):
    """Ollama provider implementation."""
    
    async def complete(self, prompt: str) -> LLMResponse:
        """Call Ollama API (local)."""
        import httpx
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "model": self.model_config["name"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": self.model_config["max_tokens"],
                "temperature": self.model_config["temperature"],
            },
        }
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data.get("response", "").strip(),
                model=self.model_config["name"],
                provider=self.provider_name,
            )





class ProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
        "zhipu": OpenAICompatibleProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str, model_config: Dict) -> LLMProvider:
        """Create provider instance based on name.
        
        If provider is not explicitly configured, use OpenAICompatibleProvider
        for providers that follow OpenAI API format.
        """
        if provider_name in cls._providers:
            provider_class = cls._providers[provider_name]
        else:
            # Default to OpenAICompatibleProvider for unknown providers
            # This allows adding new OpenAI-compatible providers without code changes
            provider_class = OpenAICompatibleProvider
        
        return provider_class(provider_name, model_config)

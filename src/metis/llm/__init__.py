"""LLM client for article summarization."""
import json
from dataclasses import dataclass
from typing import Optional

import httpx

from metis.config import settings, get_model_config


@dataclass
class LLMResponse:
    """LLM API response."""
    content: str
    model: str
    provider: str


class LLMClient:
    """Multi-provider LLM client (OpenAI, Anthropic, Ollama)."""
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model
        # Load model config from JSON
        self.model_config = get_model_config(self.provider, self.model)
    
    async def summarize(self, content: str, prompt: Optional[str] = None) -> LLMResponse:
        """Generate summary using LLM."""
        prompt_template = prompt or settings.summarization_prompt
        # Reserve ~1000 chars for prompt template + response
        max_content_len = 6000
        # Truncate content to fit within context window
        truncated_content = content[:max_content_len] if len(content) > max_content_len else content
        user_prompt = prompt_template.replace("{{content}}", truncated_content)
        
        if self.provider == "openai":
            return await self._openai_complete(user_prompt)
        elif self.provider == "anthropic":
            return await self._anthropic_complete(user_prompt)
        elif self.provider == "ollama":
            return await self._ollama_complete(user_prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    async def _openai_complete(self, prompt: str) -> LLMResponse:
        """Call OpenAI API."""
        api_key = settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
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
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=self.model,
                provider="openai",
            )
    
    async def _anthropic_complete(self, prompt: str) -> LLMResponse:
        """Call Anthropic API."""
        api_key = settings.anthropic_api_key
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
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
                model=self.model,
                provider="anthropic",
            )
    
    async def _ollama_complete(self, prompt: str) -> LLMResponse:
        """Call Ollama API (local)."""
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
                model=self.model,
                provider="ollama",
            )


# Singleton instance
llm_client = LLMClient()

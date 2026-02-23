"""LLM data models."""
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM API response."""
    content: str
    model: str
    provider: str

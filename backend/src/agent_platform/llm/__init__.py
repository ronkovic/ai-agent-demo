"""LLM module."""

from .base import ChatMessage, LLMProvider, LLMResponse
from .provider import LiteLLMProvider

__all__ = [
    "ChatMessage",
    "LLMProvider",
    "LLMResponse",
    "LiteLLMProvider",
    "get_llm_provider",
]


def get_llm_provider() -> LLMProvider:
    """Get LLM provider instance.

    Returns:
        LLMProvider instance (currently LiteLLM).
    """
    return LiteLLMProvider()

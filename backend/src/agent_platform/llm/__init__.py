"""LLM module."""

from .base import ChatMessage, LLMProvider, LLMResponse, ToolCall
from .provider import LiteLLMProvider
from .tools import to_anthropic_tools, to_litellm_tools, to_openai_tools

__all__ = [
    "ChatMessage",
    "LLMProvider",
    "LLMResponse",
    "LiteLLMProvider",
    "ToolCall",
    "get_llm_provider",
    "to_anthropic_tools",
    "to_litellm_tools",
    "to_openai_tools",
]


def get_llm_provider() -> LLMProvider:
    """Get LLM provider instance.

    Returns:
        LLMProvider instance (currently LiteLLM).
    """
    return LiteLLMProvider()

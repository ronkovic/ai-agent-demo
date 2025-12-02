"""LLM Provider base class."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Chat message structure."""

    role: str  # 'system', 'user', 'assistant'
    content: str


@dataclass
class LLMResponse:
    """LLM response structure."""

    content: str
    model: str
    usage: dict | None = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Generate a chat completion (non-streaming).

        Args:
            messages: List of chat messages.
            model: Model identifier (e.g., 'claude-3-5-sonnet-20241022').
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse with generated content.
        """
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: object,
    ) -> AsyncIterator[str]:
        """Generate a streaming chat completion.

        Args:
            messages: List of chat messages.
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional provider-specific arguments.

        Yields:
            String chunks of the generated content.
        """
        ...

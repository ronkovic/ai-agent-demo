"""LLM Provider base class."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    """Chat message structure."""

    role: str  # 'system', 'user', 'assistant', 'tool'
    content: str
    tool_call_id: str | None = None  # For tool result messages


@dataclass
class ToolCall:
    """Tool call from LLM."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    """LLM response structure."""

    content: str
    model: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: dict | None = None

    @property
    def has_tool_calls(self) -> bool:
        """Check if response has tool calls."""
        return len(self.tool_calls) > 0


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
        tools: list[dict[str, Any]] | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Generate a chat completion (non-streaming).

        Args:
            messages: List of chat messages.
            model: Model identifier (e.g., 'claude-3-5-sonnet-20241022').
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            tools: Optional list of tool definitions in LiteLLM format.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse with generated content and optional tool_calls.
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
        tools: list[dict[str, Any]] | None = None,
        **kwargs: object,
    ) -> AsyncIterator[str]:
        """Generate a streaming chat completion.

        Args:
            messages: List of chat messages.
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            tools: Optional list of tool definitions in LiteLLM format.
            **kwargs: Additional provider-specific arguments.

        Yields:
            String chunks of the generated content.
        """
        ...

    @abstractmethod
    async def chat_with_tools(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Generate a chat completion with tool support (non-streaming).

        This method returns the full response including any tool calls.
        Use this when you need to handle tool calls in a loop.

        Args:
            messages: List of chat messages.
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            tools: Optional list of tool definitions in LiteLLM format.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse with content and tool_calls if any.
        """
        ...

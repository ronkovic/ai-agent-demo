"""LiteLLM provider implementation."""

from collections.abc import AsyncIterator
from typing import Any

import litellm

from .base import ChatMessage, LLMProvider, LLMResponse


class LiteLLMProvider(LLMProvider):
    """LiteLLM provider for multi-provider LLM support.

    Supports:
    - Anthropic Claude: model="claude-3-5-sonnet-20241022"
    - OpenAI: model="gpt-4o", model="gpt-4o-mini"
    - AWS Bedrock: model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0"
    """

    def _format_messages(self, messages: list[ChatMessage]) -> list[dict[str, str]]:
        """Convert ChatMessage objects to LiteLLM format."""
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a chat completion (non-streaming).

        Args:
            messages: List of chat messages.
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse with generated content.
        """
        formatted_messages = self._format_messages(messages)

        response = await litellm.acompletion(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Extract content from response
        content = response.choices[0].message.content or ""

        # Extract usage information
        usage = None
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return LLMResponse(
            content=content,
            model=response.model or model,
            usage=usage,
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
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
        formatted_messages = self._format_messages(messages)

        response = await litellm.acompletion(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

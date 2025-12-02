"""LiteLLM provider implementation."""

import json
from collections.abc import AsyncIterator
from typing import Any

import litellm

from .base import ChatMessage, LLMProvider, LLMResponse, ToolCall


class LiteLLMProvider(LLMProvider):
    """LiteLLM provider for multi-provider LLM support.

    Supports:
    - Anthropic Claude: model="claude-3-5-sonnet-20241022"
    - OpenAI: model="gpt-4o", model="gpt-4o-mini"
    - AWS Bedrock: model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0"
    """

    def _format_messages(self, messages: list[ChatMessage]) -> list[dict[str, Any]]:
        """Convert ChatMessage objects to LiteLLM format."""
        formatted = []
        for msg in messages:
            message: dict[str, Any] = {"role": msg.role, "content": msg.content}
            # Add tool_call_id for tool result messages
            if msg.tool_call_id:
                message["tool_call_id"] = msg.tool_call_id
            formatted.append(message)
        return formatted

    def _parse_tool_calls(self, response_message: Any) -> list[ToolCall]:
        """Parse tool calls from LLM response.

        Args:
            response_message: The message object from LLM response.

        Returns:
            List of ToolCall objects.
        """
        tool_calls = []
        if hasattr(response_message, "tool_calls") and response_message.tool_calls:
            for tc in response_message.tool_calls:
                # Parse arguments from JSON string
                arguments = {}
                if tc.function.arguments:
                    try:
                        arguments = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {"raw": tc.function.arguments}

                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=arguments,
                    )
                )
        return tool_calls

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a chat completion (non-streaming).

        Args:
            messages: List of chat messages.
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            tools: Optional list of tool definitions.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse with generated content.
        """
        formatted_messages = self._format_messages(messages)

        # Build request parameters
        request_params: dict[str, Any] = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        # Add tools if provided
        if tools:
            request_params["tools"] = tools

        response = await litellm.acompletion(**request_params)

        # Extract content from response
        content = response.choices[0].message.content or ""

        # Parse tool calls
        tool_calls = self._parse_tool_calls(response.choices[0].message)

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
            tool_calls=tool_calls,
            usage=usage,
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Generate a streaming chat completion.

        Note: When tools are provided and the LLM decides to call tools,
        streaming may not yield content. Use chat_with_tools for tool handling.

        Args:
            messages: List of chat messages.
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            tools: Optional list of tool definitions.
            **kwargs: Additional provider-specific arguments.

        Yields:
            String chunks of the generated content.
        """
        formatted_messages = self._format_messages(messages)

        # Build request parameters
        request_params: dict[str, Any] = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs,
        }

        # Add tools if provided
        if tools:
            request_params["tools"] = tools

        response = await litellm.acompletion(**request_params)

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

    async def chat_with_tools(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a chat completion with tool support.

        This is the same as chat() but explicitly named for tool handling.

        Args:
            messages: List of chat messages.
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            tools: Optional list of tool definitions.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse with content and tool_calls if any.
        """
        return await self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs,
        )

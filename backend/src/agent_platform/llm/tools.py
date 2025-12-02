"""LLMツールフォーマッター.

各LLMプロバイダー向けにツール定義を変換する。
"""

from typing import Any

from ..tools.base import ToolDefinition


def to_anthropic_tools(definitions: list[ToolDefinition]) -> list[dict[str, Any]]:
    """Convert tool definitions to Claude's tool format.

    Args:
        definitions: List of ToolDefinition.

    Returns:
        List of tools in Anthropic/Claude format.
    """
    tools = []
    for d in definitions:
        tool = {
            "name": d.name,
            "description": d.description,
            "input_schema": d.to_json_schema(),
        }
        tools.append(tool)
    return tools


def to_openai_tools(definitions: list[ToolDefinition]) -> list[dict[str, Any]]:
    """Convert tool definitions to OpenAI's function calling format.

    Args:
        definitions: List of ToolDefinition.

    Returns:
        List of tools in OpenAI format.
    """
    tools = []
    for d in definitions:
        tool = {
            "type": "function",
            "function": {
                "name": d.name,
                "description": d.description,
                "parameters": d.to_json_schema(),
            },
        }
        tools.append(tool)
    return tools


def to_litellm_tools(
    definitions: list[ToolDefinition], provider: str = "anthropic"
) -> list[dict[str, Any]]:
    """Convert tool definitions to LiteLLM format.

    LiteLLM handles the conversion internally, but we use OpenAI format
    as it's the most widely supported.

    Args:
        definitions: List of ToolDefinition.
        provider: LLM provider name ('anthropic', 'openai', etc.)

    Returns:
        List of tools in LiteLLM-compatible format.
    """
    # LiteLLM uses OpenAI format internally for most providers
    return to_openai_tools(definitions)

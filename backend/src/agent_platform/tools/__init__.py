"""ツールモジュール."""

from .base import BaseTool, ToolDefinition, ToolParameter, ToolResult
from .code import CodeExecutionTool, get_code_execution_tool, register_code_execution_tool
from .registry import ToolRegistry
from .web import (
    MockSearchProvider,
    WebSearchProvider,
    WebSearchTool,
    get_web_search_tool,
    register_web_search_tool,
)

__all__ = [
    # Base
    "BaseTool",
    "ToolDefinition",
    "ToolParameter",
    "ToolResult",
    "ToolRegistry",
    # Code execution
    "CodeExecutionTool",
    "get_code_execution_tool",
    "register_code_execution_tool",
    # Web search
    "WebSearchProvider",
    "MockSearchProvider",
    "WebSearchTool",
    "get_web_search_tool",
    "register_web_search_tool",
]


def register_default_tools() -> None:
    """Register all default tools to the registry.

    Call this function during application startup to make tools available.
    """
    register_code_execution_tool()
    register_web_search_tool()

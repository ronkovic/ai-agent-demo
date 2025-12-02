"""ツールレジストリ."""

from typing import ClassVar

from .base import BaseTool, ToolDefinition


class ToolRegistry:
    """ツールレジストリ - 利用可能なツールを管理."""

    _tools: ClassVar[dict[str, BaseTool]] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        """Register a tool.

        Args:
            tool: Tool instance to register.
        """
        cls._tools[tool.name] = tool

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a tool.

        Args:
            name: Tool name to unregister.
        """
        cls._tools.pop(name, None)

    @classmethod
    def get(cls, name: str) -> BaseTool | None:
        """Get a tool by name.

        Args:
            name: Tool name.

        Returns:
            Tool instance or None if not found.
        """
        return cls._tools.get(name)

    @classmethod
    def get_definitions(cls, tool_names: list[str]) -> list[ToolDefinition]:
        """Get tool definitions for specified tool names.

        Args:
            tool_names: List of tool names.

        Returns:
            List of ToolDefinition for registered tools.
        """
        definitions = []
        for name in tool_names:
            tool = cls._tools.get(name)
            if tool:
                definitions.append(tool.definition)
        return definitions

    @classmethod
    def get_all_definitions(cls) -> list[ToolDefinition]:
        """Get all registered tool definitions.

        Returns:
            List of all ToolDefinition.
        """
        return [tool.definition for tool in cls._tools.values()]

    @classmethod
    def list_all(cls) -> list[str]:
        """List all registered tool names.

        Returns:
            List of tool names.
        """
        return list(cls._tools.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools."""
        cls._tools.clear()

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a tool is registered.

        Args:
            name: Tool name.

        Returns:
            True if registered.
        """
        return name in cls._tools

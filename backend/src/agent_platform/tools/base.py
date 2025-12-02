"""ツール基盤クラス・型定義."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolParameter:
    """ツールパラメータ定義."""

    name: str
    type: str  # 'string', 'number', 'integer', 'boolean', 'array', 'object'
    description: str
    required: bool = True
    enum: list[str] | None = None
    default: Any = None


@dataclass
class ToolDefinition:
    """ツール定義."""

    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON Schema format."""
        properties = {}
        required = []

        for param in self.parameters:
            prop: dict[str, Any] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default

            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


@dataclass
class ToolResult:
    """ツール実行結果."""

    success: bool
    output: Any
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "success": self.success,
            "output": self.output,
        }
        if self.error:
            result["error"] = self.error
        return result


class BaseTool(ABC):
    """ツール基底クラス."""

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Return tool definition for LLM.

        Returns:
            ToolDefinition with name, description, and parameters.
        """
        ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters.

        Returns:
            ToolResult with success status and output/error.
        """
        ...

    @property
    def name(self) -> str:
        """Get tool name."""
        return self.definition.name

"""Tests for the tools module."""

import pytest

from agent_platform.tools import (
    BaseTool,
    ToolDefinition,
    ToolParameter,
    ToolRegistry,
    ToolResult,
)
from agent_platform.tools.code import CodeExecutionTool
from agent_platform.tools.web import MockSearchProvider, WebSearchTool


class TestToolDefinition:
    """Tests for ToolDefinition."""

    def test_to_json_schema_simple(self):
        """Test JSON schema generation for simple tool."""
        definition = ToolDefinition(
            name="test_tool",
            description="A test tool",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True,
                ),
            ],
        )

        schema = definition.to_json_schema()

        # to_json_schema returns the parameters schema (not the full tool format)
        assert schema["type"] == "object"
        assert "query" in schema["properties"]
        assert schema["required"] == ["query"]

    def test_to_json_schema_with_enum(self):
        """Test JSON schema generation with enum parameter."""
        definition = ToolDefinition(
            name="lang_tool",
            description="Language tool",
            parameters=[
                ToolParameter(
                    name="language",
                    type="string",
                    description="Programming language",
                    required=True,
                    enum=["python", "javascript"],
                ),
            ],
        )

        schema = definition.to_json_schema()
        lang_prop = schema["properties"]["language"]

        assert lang_prop["enum"] == ["python", "javascript"]

    def test_to_json_schema_optional_params(self):
        """Test JSON schema generation with optional parameters."""
        definition = ToolDefinition(
            name="search",
            description="Search tool",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Query",
                    required=True,
                ),
                ToolParameter(
                    name="limit",
                    type="integer",
                    description="Result limit",
                    required=False,
                    default=10,
                ),
            ],
        )

        schema = definition.to_json_schema()

        assert "query" in schema["required"]
        assert "limit" not in schema["required"]


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def setup_method(self):
        """Clear registry before each test."""
        ToolRegistry._tools.clear()

    def test_register_and_get(self):
        """Test registering and retrieving a tool."""
        tool = WebSearchTool(provider=MockSearchProvider())
        ToolRegistry.register(tool)

        retrieved = ToolRegistry.get("web_search")
        assert retrieved is tool

    def test_get_nonexistent(self):
        """Test getting a non-existent tool."""
        result = ToolRegistry.get("nonexistent")
        assert result is None

    def test_list_all(self):
        """Test listing all registered tools."""
        tool1 = WebSearchTool(provider=MockSearchProvider())
        tool2 = CodeExecutionTool()

        ToolRegistry.register(tool1)
        ToolRegistry.register(tool2)

        tools = ToolRegistry.list_all()
        assert len(tools) == 2
        assert "web_search" in tools
        assert "execute_code" in tools

    def test_get_definitions(self):
        """Test getting definitions for specific tools."""
        tool = WebSearchTool(provider=MockSearchProvider())
        ToolRegistry.register(tool)

        definitions = ToolRegistry.get_definitions(["web_search"])
        assert len(definitions) == 1
        assert definitions[0].name == "web_search"

    def test_get_definitions_nonexistent(self):
        """Test getting definitions for non-existent tools."""
        definitions = ToolRegistry.get_definitions(["nonexistent"])
        assert len(definitions) == 0

    def test_get_all_definitions(self):
        """Test getting all tool definitions."""
        tool1 = WebSearchTool(provider=MockSearchProvider())
        tool2 = CodeExecutionTool()

        ToolRegistry.register(tool1)
        ToolRegistry.register(tool2)

        definitions = ToolRegistry.get_all_definitions()
        assert len(definitions) == 2


class TestToolResult:
    """Tests for ToolResult."""

    def test_success_result(self):
        """Test creating a success result."""
        result = ToolResult(success=True, output={"data": "test"})

        assert result.success is True
        assert result.output == {"data": "test"}
        assert result.error is None

    def test_error_result(self):
        """Test creating an error result."""
        result = ToolResult(success=False, output=None, error="Something went wrong")

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.output is None

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ToolResult(success=True, output="test output")
        d = result.to_dict()

        assert d["success"] is True
        assert d["output"] == "test output"
        assert "error" not in d

    def test_to_dict_with_error(self):
        """Test converting error result to dictionary."""
        result = ToolResult(success=False, output=None, error="Error message")
        d = result.to_dict()

        assert d["success"] is False
        assert d["error"] == "Error message"


class TestWebSearchTool:
    """Tests for WebSearchTool."""

    @pytest.mark.asyncio
    async def test_web_search_with_mock_provider(self):
        """Test web search with mock provider."""
        provider = MockSearchProvider()
        tool = WebSearchTool(provider=provider)

        result = await tool.execute(query="test query", max_results=3)

        assert result.success is True
        assert isinstance(result.output, dict)
        assert result.output["query"] == "test query"
        assert result.output["provider"] == "mock"
        assert len(result.output["results"]) <= 3

    @pytest.mark.asyncio
    async def test_web_search_empty_query(self):
        """Test web search with empty query."""
        provider = MockSearchProvider()
        tool = WebSearchTool(provider=provider)

        result = await tool.execute(query="", max_results=5)

        # Empty query should fail
        assert result.success is False
        assert "empty" in result.error.lower()

    def test_web_search_definition(self):
        """Test web search tool definition."""
        tool = WebSearchTool(provider=MockSearchProvider())
        definition = tool.definition

        assert definition.name == "web_search"
        assert len(definition.parameters) == 2
        param_names = [p.name for p in definition.parameters]
        assert "query" in param_names
        assert "max_results" in param_names


class TestCodeExecutionTool:
    """Tests for CodeExecutionTool."""

    def test_code_execution_definition(self):
        """Test code execution tool definition."""
        tool = CodeExecutionTool()
        definition = tool.definition

        assert definition.name == "execute_code"
        assert len(definition.parameters) == 2
        param_names = [p.name for p in definition.parameters]
        assert "language" in param_names
        assert "code" in param_names

    def test_code_execution_language_enum(self):
        """Test that language parameter has correct enum values."""
        tool = CodeExecutionTool()
        definition = tool.definition

        lang_param = next(p for p in definition.parameters if p.name == "language")
        assert lang_param.enum is not None
        assert "python" in lang_param.enum
        assert "javascript" in lang_param.enum

    @pytest.mark.asyncio
    async def test_code_execution_unsupported_language(self):
        """Test code execution with unsupported language."""
        tool = CodeExecutionTool()

        result = await tool.execute(language="ruby", code="puts 'hello'")

        assert result.success is False
        assert "unsupported" in result.error.lower()

    # Note: Full Docker-based tests require Docker to be running
    # and are better suited for integration tests

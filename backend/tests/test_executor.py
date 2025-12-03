"""Tests for the ToolExecutor."""

import pytest

from agent_platform.core.executor import MAX_TOOL_CALLS_PER_TURN, ToolExecutor
from agent_platform.tools import ToolRegistry
from agent_platform.tools.web import MockSearchProvider, WebSearchTool


class TestToolExecutor:
    """Tests for ToolExecutor."""

    def setup_method(self):
        """Set up test fixtures."""
        ToolRegistry._tools.clear()
        # Register mock web search tool
        tool = WebSearchTool(provider=MockSearchProvider())
        ToolRegistry.register(tool)

    @pytest.mark.asyncio
    async def test_execute_registered_tool(self):
        """Test executing a registered tool."""
        executor = ToolExecutor()

        result = await executor.execute(
            tool_name="web_search",
            arguments={"query": "test", "max_results": 3},
        )

        assert result.success is True
        assert isinstance(result.output, dict)
        assert result.output["query"] == "test"

    @pytest.mark.asyncio
    async def test_execute_unregistered_tool(self):
        """Test executing an unregistered tool."""
        executor = ToolExecutor()

        result = await executor.execute(
            tool_name="nonexistent_tool",
            arguments={},
        )

        assert result.success is False
        assert "unknown" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_parallel(self):
        """Test parallel tool execution."""
        executor = ToolExecutor()

        calls = [
            ("web_search", {"query": "query1", "max_results": 2}),
            ("web_search", {"query": "query2", "max_results": 2}),
            ("web_search", {"query": "query3", "max_results": 2}),
        ]

        results = await executor.execute_parallel(calls)

        assert len(results) == 3
        for result in results:
            assert result.success is True

    @pytest.mark.asyncio
    async def test_tool_call_limit(self):
        """Test that tool calls are limited per turn."""
        executor = ToolExecutor(max_calls=MAX_TOOL_CALLS_PER_TURN)

        # Try to exceed the limit
        calls = [
            ("web_search", {"query": f"query{i}", "max_results": 1})
            for i in range(MAX_TOOL_CALLS_PER_TURN + 2)
        ]

        results = await executor.execute_parallel(calls)

        # Should return results for all (executed + error results for overflow)
        assert len(results) == MAX_TOOL_CALLS_PER_TURN + 2

        # First MAX_TOOL_CALLS_PER_TURN should succeed
        successful = sum(1 for r in results if r.success)
        assert successful == MAX_TOOL_CALLS_PER_TURN

    @pytest.mark.asyncio
    async def test_execute_with_missing_arguments(self):
        """Test executing tool with missing required arguments."""
        executor = ToolExecutor()

        # web_search requires 'query' argument - missing query should fail
        result = await executor.execute(
            tool_name="web_search",
            arguments={},  # Missing 'query'
        )

        # The tool should return error for missing required argument
        assert result.success is False

    @pytest.mark.asyncio
    async def test_calls_remaining(self):
        """Test tracking remaining calls."""
        executor = ToolExecutor(max_calls=3)

        assert executor.calls_remaining == 3
        assert executor.calls_made == 0

        await executor.execute("web_search", {"query": "test1"})
        assert executor.calls_remaining == 2
        assert executor.calls_made == 1

        await executor.execute("web_search", {"query": "test2"})
        assert executor.calls_remaining == 1
        assert executor.calls_made == 2

    @pytest.mark.asyncio
    async def test_reset_call_count(self):
        """Test resetting call count."""
        executor = ToolExecutor(max_calls=3)

        await executor.execute("web_search", {"query": "test"})
        assert executor.calls_made == 1

        executor.reset_call_count()
        assert executor.calls_made == 0
        assert executor.calls_remaining == 3


class TestToolExecutorTimeout:
    """Tests for ToolExecutor timeout handling."""

    def setup_method(self):
        """Set up test fixtures."""
        ToolRegistry._tools.clear()

    # Note: Timeout tests would require a slow/blocking mock tool
    # which is better suited for integration tests with actual async operations

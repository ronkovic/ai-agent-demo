"""ツール実行エンジン."""

import asyncio
import logging
from typing import Any

from ..tools.base import ToolResult
from ..tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

# ツール実行の制限
MAX_TOOL_CALLS_PER_TURN = 5
DEFAULT_TIMEOUT_SECONDS = 60


class ToolExecutionError(Exception):
    """ツール実行エラー."""

    pass


class ToolExecutor:
    """ツール実行エンジン.

    ツールの実行を管理し、タイムアウトや並列実行を制御する。
    """

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_calls: int = MAX_TOOL_CALLS_PER_TURN,
    ):
        """Initialize executor.

        Args:
            timeout: Default timeout for tool execution in seconds.
            max_calls: Maximum number of tool calls per turn.
        """
        self.timeout = timeout
        self.max_calls = max_calls
        self._call_count = 0

    def reset_call_count(self) -> None:
        """Reset the call counter for a new turn."""
        self._call_count = 0

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        timeout: float | None = None,
    ) -> ToolResult:
        """Execute a single tool.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Arguments to pass to the tool.
            timeout: Optional timeout override.

        Returns:
            ToolResult with execution outcome.
        """
        # Check call limit
        if self._call_count >= self.max_calls:
            logger.warning(f"Tool call limit reached ({self.max_calls})")
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool call limit reached ({self.max_calls} calls per turn)",
            )

        # Get tool from registry
        tool = ToolRegistry.get(tool_name)
        if not tool:
            logger.error(f"Unknown tool: {tool_name}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Unknown tool: {tool_name}",
            )

        # Execute with timeout
        effective_timeout = timeout or self.timeout
        try:
            logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            self._call_count += 1

            result = await asyncio.wait_for(
                tool.execute(**arguments),
                timeout=effective_timeout,
            )

            logger.info(f"Tool {tool_name} completed: success={result.success}")
            return result

        except TimeoutError:
            logger.error(f"Tool {tool_name} timed out after {effective_timeout}s")
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool execution timed out after {effective_timeout} seconds",
            )
        except TypeError as e:
            # Invalid arguments
            logger.error(f"Tool {tool_name} invalid arguments: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Invalid arguments: {e}",
            )
        except Exception as e:
            logger.exception(f"Tool {tool_name} execution failed: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Execution error: {e}",
            )

    async def execute_parallel(
        self,
        calls: list[tuple[str, dict[str, Any]]],
        timeout: float | None = None,
    ) -> list[ToolResult]:
        """Execute multiple tools in parallel.

        Args:
            calls: List of (tool_name, arguments) tuples.
            timeout: Optional timeout override for each tool.

        Returns:
            List of ToolResult in the same order as calls.
        """
        if not calls:
            return []

        # Check if we can execute all calls
        remaining_calls = self.max_calls - self._call_count
        if len(calls) > remaining_calls:
            logger.warning(
                f"Too many tool calls: {len(calls)} requested, {remaining_calls} remaining"
            )
            # Execute what we can and return errors for the rest
            executable = calls[:remaining_calls]
            overflow = calls[remaining_calls:]

            results = await self._execute_batch(executable, timeout)

            # Add error results for overflow
            for tool_name, _ in overflow:
                results.append(
                    ToolResult(
                        success=False,
                        output=None,
                        error=f"Tool call limit reached, {tool_name} not executed",
                    )
                )
            return results

        return await self._execute_batch(calls, timeout)

    async def _execute_batch(
        self,
        calls: list[tuple[str, dict[str, Any]]],
        timeout: float | None = None,
    ) -> list[ToolResult]:
        """Execute a batch of tool calls.

        Args:
            calls: List of (tool_name, arguments) tuples.
            timeout: Optional timeout override.

        Returns:
            List of ToolResult.
        """
        tasks = [
            self.execute(tool_name, arguments, timeout)
            for tool_name, arguments in calls
        ]
        return await asyncio.gather(*tasks)

    @property
    def calls_remaining(self) -> int:
        """Get the number of tool calls remaining."""
        return max(0, self.max_calls - self._call_count)

    @property
    def calls_made(self) -> int:
        """Get the number of tool calls made."""
        return self._call_count

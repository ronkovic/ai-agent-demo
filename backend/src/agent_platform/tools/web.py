"""Web検索ツール.

抽象化された検索プロバイダーインターフェースと
モック実装を提供する。将来的にTavily/SerpAPI/DuckDuckGo等を追加可能。
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from .base import BaseTool, ToolDefinition, ToolParameter, ToolResult

logger = logging.getLogger(__name__)


class WebSearchProvider(ABC):
    """Web検索プロバイダーの抽象基底クラス."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Execute a web search.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.

        Returns:
            List of search results, each containing:
            - title: Result title
            - url: Result URL
            - snippet: Text snippet/description
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for identification."""
        ...


class MockSearchProvider(WebSearchProvider):
    """モック検索プロバイダー（開発・テスト用）."""

    @property
    def name(self) -> str:
        return "mock"

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Return mock search results.

        Args:
            query: Search query string.
            max_results: Maximum number of results.

        Returns:
            List of mock search results.
        """
        # Generate mock results based on query
        results = []
        for i in range(min(max_results, 3)):
            results.append(
                {
                    "title": f"Mock Result {i + 1} for '{query}'",
                    "url": f"https://example.com/search?q={query.replace(' ', '+')}&page={i + 1}",
                    "snippet": f"This is a mock search result #{i + 1} for the query: {query}. "
                    "This provider is for development and testing purposes only.",
                }
            )
        return results


class WebSearchTool(BaseTool):
    """Web検索ツール.

    設定された検索プロバイダーを使用してWeb検索を実行する。
    """

    def __init__(self, provider: WebSearchProvider | None = None):
        """Initialize web search tool.

        Args:
            provider: Search provider to use. If None, a mock provider is used.
        """
        self._provider = provider or MockSearchProvider()

    @property
    def provider(self) -> WebSearchProvider:
        """Get the current search provider."""
        return self._provider

    @provider.setter
    def provider(self, value: WebSearchProvider) -> None:
        """Set the search provider."""
        self._provider = value

    @property
    def definition(self) -> ToolDefinition:
        """Return tool definition for LLM."""
        return ToolDefinition(
            name="web_search",
            description=(
                "Search the web for information on a given topic. "
                "Returns a list of relevant web pages with titles, URLs, and snippets. "
                "Use this to find current information, facts, or resources."
            ),
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="The search query to find information about",
                ),
                ToolParameter(
                    name="max_results",
                    type="integer",
                    description="Maximum number of results to return (1-10)",
                    required=False,
                    default=5,
                ),
            ],
        )

    async def execute(
        self, query: str, max_results: int = 5, **kwargs: Any
    ) -> ToolResult:
        """Execute a web search.

        Args:
            query: Search query string.
            max_results: Maximum number of results (clamped to 1-10).
            **kwargs: Additional arguments (ignored).

        Returns:
            ToolResult with search results or error.
        """
        # Validate query
        if not query or not query.strip():
            return ToolResult(
                success=False,
                output=None,
                error="Empty search query provided",
            )

        # Clamp max_results
        max_results = max(1, min(10, max_results))

        try:
            logger.info(
                f"Executing web search: '{query}' "
                f"(provider={self._provider.name}, max_results={max_results})"
            )
            results = await self._provider.search(query, max_results)

            return ToolResult(
                success=True,
                output={
                    "query": query,
                    "provider": self._provider.name,
                    "results": results,
                    "count": len(results),
                },
            )

        except Exception as e:
            logger.exception(f"Web search failed: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Search failed: {e}",
            )


# =============================================================================
# 将来的なプロバイダー実装例（コメントアウト）
# =============================================================================

# class TavilySearchProvider(WebSearchProvider):
#     """Tavily API検索プロバイダー."""
#
#     def __init__(self, api_key: str):
#         self._api_key = api_key
#
#     @property
#     def name(self) -> str:
#         return "tavily"
#
#     async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
#         # Tavily API実装
#         pass


# class DuckDuckGoSearchProvider(WebSearchProvider):
#     """DuckDuckGo検索プロバイダー（無料）."""
#
#     @property
#     def name(self) -> str:
#         return "duckduckgo"
#
#     async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
#         # DuckDuckGo API実装
#         pass


# =============================================================================
# ツール登録
# =============================================================================

_web_search_tool_instance: WebSearchTool | None = None


def get_web_search_tool() -> WebSearchTool:
    """Get singleton web search tool instance."""
    global _web_search_tool_instance
    if _web_search_tool_instance is None:
        _web_search_tool_instance = WebSearchTool()
    return _web_search_tool_instance


def register_web_search_tool(provider: WebSearchProvider | None = None) -> None:
    """Register web search tool to the registry.

    Args:
        provider: Optional custom search provider.
    """
    from .registry import ToolRegistry

    global _web_search_tool_instance
    _web_search_tool_instance = WebSearchTool(provider)
    ToolRegistry.register(_web_search_tool_instance)

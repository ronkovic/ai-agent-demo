"""A2Aエージェント呼び出しツール.

他のA2Aエージェントを呼び出すためのツール。
"""

import logging
from typing import Any

from ..a2a.client import A2AClient, A2AClientError, get_a2a_client
from .base import BaseTool, ToolDefinition, ToolParameter, ToolResult
from .registry import ToolRegistry

logger = logging.getLogger(__name__)


class InvokeAgentTool(BaseTool):
    """他のA2Aエージェントを呼び出すツール."""

    def __init__(self, client: A2AClient | None = None) -> None:
        """Initialize the tool.

        Args:
            client: Optional A2A client instance.
        """
        self._client = client

    @property
    def _a2a_client(self) -> A2AClient:
        """Get the A2A client."""
        if self._client is None:
            self._client = get_a2a_client()
        return self._client

    @property
    def definition(self) -> ToolDefinition:
        """Return tool definition for LLM."""
        return ToolDefinition(
            name="invoke_agent",
            description=(
                "他のAIエージェントを呼び出してタスクを依頼します。"
                "指定されたエージェントURLにA2Aプロトコルでメッセージを送信し、"
                "レスポンスを取得します。"
            ),
            parameters=[
                ToolParameter(
                    name="agent_url",
                    type="string",
                    description=(
                        "呼び出すエージェントのURL。"
                        "例: http://localhost:8000/a2a/agents/{agent_id}"
                    ),
                    required=True,
                ),
                ToolParameter(
                    name="message",
                    type="string",
                    description="エージェントに送信するメッセージまたはタスクの説明",
                    required=True,
                ),
                ToolParameter(
                    name="wait_for_completion",
                    type="boolean",
                    description="タスクの完了を待つかどうか。Falseの場合はタスクIDのみ返します",
                    required=False,
                    default=True,
                ),
            ],
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool.

        Args:
            **kwargs: Tool parameters.
                - agent_url: Target agent URL
                - message: Message to send
                - wait_for_completion: Whether to wait for completion

        Returns:
            ToolResult with agent response or task ID.
        """
        agent_url = kwargs.get("agent_url")
        message = kwargs.get("message")
        wait_for_completion = kwargs.get("wait_for_completion", True)

        if not agent_url:
            return ToolResult(
                success=False,
                output=None,
                error="agent_url is required",
            )

        if not message:
            return ToolResult(
                success=False,
                output=None,
                error="message is required",
            )

        try:
            # まずエージェントカードを取得して存在確認
            try:
                agent_card = await self._a2a_client.get_agent_card(agent_url)
                agent_name = agent_card.get("name", "Unknown Agent")
                logger.info(f"Invoking agent: {agent_name} at {agent_url}")
            except A2AClientError as e:
                if e.status_code == 404:
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"Agent not found at {agent_url}",
                    )
                # カード取得失敗でも続行（オプション）
                logger.warning(f"Could not fetch agent card: {e}")
                agent_name = "Unknown Agent"

            # タスクを送信
            result = await self._a2a_client.send_task(agent_url, message)

            task_id = result.get("id")
            task_status = result.get("status")

            # wait_for_completion=Falseの場合はタスクIDのみ返す
            if not wait_for_completion:
                return ToolResult(
                    success=True,
                    output={
                        "task_id": task_id,
                        "status": task_status,
                        "agent_name": agent_name,
                        "message": f"Task submitted to {agent_name}",
                    },
                )

            # 完了済みの場合は結果を返す
            if task_status == "completed":
                response_text = self._extract_response_text(result)
                return ToolResult(
                    success=True,
                    output={
                        "task_id": task_id,
                        "status": "completed",
                        "agent_name": agent_name,
                        "response": response_text,
                    },
                )

            # 失敗の場合
            if task_status == "failed":
                error_msg = result.get("error", "Unknown error")
                return ToolResult(
                    success=False,
                    output={"task_id": task_id, "status": "failed"},
                    error=f"Agent task failed: {error_msg}",
                )

            # まだ実行中の場合（非同期実行の場合）
            return ToolResult(
                success=True,
                output={
                    "task_id": task_id,
                    "status": task_status,
                    "agent_name": agent_name,
                    "message": f"Task is {task_status}. Use task_id to check status later.",
                },
            )

        except A2AClientError as e:
            logger.error(f"A2A client error: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Failed to invoke agent: {e}",
            )
        except Exception as e:
            logger.exception(f"Unexpected error invoking agent: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Unexpected error: {e}",
            )

    def _extract_response_text(self, result: dict[str, Any]) -> str:
        """タスク結果からレスポンステキストを抽出.

        Args:
            result: Task result dictionary.

        Returns:
            Extracted text response.
        """
        # result.message.parts からテキストを抽出
        task_result = result.get("result", {})
        message = task_result.get("message", {})
        parts = message.get("parts", [])

        texts = []
        for part in parts:
            if isinstance(part, dict):
                if part.get("type") == "text" or "text" in part:
                    texts.append(part.get("text", ""))
            elif isinstance(part, str):
                texts.append(part)

        return " ".join(texts).strip() if texts else str(task_result)


def register_invoke_agent_tool(client: A2AClient | None = None) -> None:
    """invoke_agentツールを登録する.

    Args:
        client: Optional A2A client instance for testing.
    """
    tool = InvokeAgentTool(client=client)
    ToolRegistry.register(tool)

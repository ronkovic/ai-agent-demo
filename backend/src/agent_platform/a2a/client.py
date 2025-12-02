"""A2Aクライアント実装.

他のA2Aエージェントと通信するためのクライアント。
"""

import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# デフォルトタイムアウト設定
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
STREAMING_TIMEOUT = httpx.Timeout(120.0, connect=10.0)


class A2AClientError(Exception):
    """A2Aクライアントエラー."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize error.

        Args:
            message: Error message.
            status_code: HTTP status code if applicable.
        """
        super().__init__(message)
        self.status_code = status_code


class A2AClient:
    """A2Aクライアント.

    他のA2Aエージェントを呼び出すためのクライアント実装。
    """

    def __init__(self, timeout: httpx.Timeout | None = None) -> None:
        """Initialize A2A client.

        Args:
            timeout: Custom timeout settings.
        """
        self._timeout = timeout or DEFAULT_TIMEOUT

    async def get_agent_card(self, agent_url: str) -> dict[str, Any]:
        """エージェントカードを取得する.

        Args:
            agent_url: エージェントのベースURL

        Returns:
            エージェントカード辞書

        Raises:
            A2AClientError: 取得に失敗した場合
        """
        # URLを正規化
        base_url = agent_url.rstrip("/")

        # /.well-known/agent.json エンドポイントを構築
        card_url = f"{base_url}/.well-known/agent.json"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(card_url)

                if response.status_code == 404:
                    raise A2AClientError(
                        f"Agent card not found at {card_url}", status_code=404
                    )

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting agent card: {e}")
            raise A2AClientError(
                f"Failed to get agent card: {e}", status_code=e.response.status_code
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error getting agent card: {e}")
            raise A2AClientError(f"Failed to connect to agent: {e}") from e

    async def send_task(
        self,
        agent_url: str,
        message: str,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """エージェントにタスクを送信する（非ストリーミング）.

        Args:
            agent_url: エージェントのベースURL
            message: 送信するメッセージ
            task_id: オプションのタスクID

        Returns:
            タスク結果

        Raises:
            A2AClientError: 送信に失敗した場合
        """
        base_url = agent_url.rstrip("/")
        tasks_url = f"{base_url}/tasks"

        # A2Aタスクリクエストを構築
        request_body: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}],
            }
        }

        if task_id:
            request_body["id"] = task_id

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(tasks_url, json=request_body)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending task: {e}")
            raise A2AClientError(
                f"Failed to send task: {e}", status_code=e.response.status_code
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error sending task: {e}")
            raise A2AClientError(f"Failed to connect to agent: {e}") from e

    async def send_task_streaming(
        self,
        agent_url: str,
        message: str,
        task_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """エージェントにタスクを送信する（SSEストリーミング）.

        Args:
            agent_url: エージェントのベースURL
            message: 送信するメッセージ
            task_id: オプションのタスクID

        Yields:
            ストリーミングイベント

        Raises:
            A2AClientError: 送信に失敗した場合
        """
        base_url = agent_url.rstrip("/")
        tasks_url = f"{base_url}/tasks"

        request_body: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}],
            }
        }

        if task_id:
            request_body["id"] = task_id

        try:
            async with httpx.AsyncClient(timeout=STREAMING_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    tasks_url,
                    json=request_body,
                    headers={"Accept": "text/event-stream"},
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # "data: " を除去
                            if data.strip():
                                try:
                                    import json

                                    yield json.loads(data)
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to parse SSE data: {data}")
                                    continue

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error in streaming task: {e}")
            raise A2AClientError(
                f"Failed to stream task: {e}", status_code=e.response.status_code
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error in streaming task: {e}")
            raise A2AClientError(f"Failed to connect to agent: {e}") from e

    async def get_task_status(
        self,
        agent_url: str,
        task_id: str,
    ) -> dict[str, Any]:
        """タスクのステータスを取得する.

        Args:
            agent_url: エージェントのベースURL
            task_id: タスクID

        Returns:
            タスクステータス

        Raises:
            A2AClientError: 取得に失敗した場合
        """
        base_url = agent_url.rstrip("/")
        status_url = f"{base_url}/tasks/{task_id}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(status_url)

                if response.status_code == 404:
                    raise A2AClientError(
                        f"Task {task_id} not found", status_code=404
                    )

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting task status: {e}")
            raise A2AClientError(
                f"Failed to get task status: {e}", status_code=e.response.status_code
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error getting task status: {e}")
            raise A2AClientError(f"Failed to connect to agent: {e}") from e

    async def cancel_task(
        self,
        agent_url: str,
        task_id: str,
    ) -> dict[str, Any]:
        """タスクをキャンセルする.

        Args:
            agent_url: エージェントのベースURL
            task_id: タスクID

        Returns:
            キャンセル結果

        Raises:
            A2AClientError: キャンセルに失敗した場合
        """
        base_url = agent_url.rstrip("/")
        cancel_url = f"{base_url}/tasks/{task_id}/cancel"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(cancel_url)

                if response.status_code == 404:
                    raise A2AClientError(
                        f"Task {task_id} not found", status_code=404
                    )

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error cancelling task: {e}")
            raise A2AClientError(
                f"Failed to cancel task: {e}", status_code=e.response.status_code
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error cancelling task: {e}")
            raise A2AClientError(f"Failed to connect to agent: {e}") from e


# グローバルクライアントインスタンス
_default_client: A2AClient | None = None


def get_a2a_client() -> A2AClient:
    """デフォルトA2Aクライアントを取得する.

    Returns:
        A2Aクライアントインスタンス
    """
    global _default_client
    if _default_client is None:
        _default_client = A2AClient()
    return _default_client

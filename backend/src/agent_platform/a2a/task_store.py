"""A2Aタスクストレージ.

タスクの状態管理とconversation_idとのマッピングを提供する。
本番環境ではRedisやデータベースバックエンドに置き換え推奨。
"""

import asyncio
from typing import Any
from uuid import UUID

from .types import A2ATaskContext, A2ATaskStatus


class TaskStore:
    """インメモリタスクストア.

    A2Aタスクの状態を管理し、内部会話とのマッピングを維持する。
    """

    def __init__(self) -> None:
        """Initialize the task store."""
        self._tasks: dict[str, dict[str, Any]] = {}
        self._contexts: dict[str, A2ATaskContext] = {}
        self._lock = asyncio.Lock()

    async def get_task(self, task_id: str) -> dict[str, Any] | None:
        """タスクをIDで取得.

        Args:
            task_id: タスクID

        Returns:
            タスクデータまたはNone
        """
        async with self._lock:
            return self._tasks.get(task_id)

    async def save_task(self, task_id: str, task_data: dict[str, Any]) -> None:
        """タスクを保存または更新.

        Args:
            task_id: タスクID
            task_data: タスクデータ
        """
        async with self._lock:
            self._tasks[task_id] = task_data

    async def delete_task(self, task_id: str) -> None:
        """タスクとそのコンテキストを削除.

        Args:
            task_id: タスクID
        """
        async with self._lock:
            self._tasks.pop(task_id, None)
            self._contexts.pop(task_id, None)

    async def get_context(self, task_id: str) -> A2ATaskContext | None:
        """タスクコンテキストを取得.

        Args:
            task_id: タスクID

        Returns:
            タスクコンテキストまたはNone
        """
        async with self._lock:
            return self._contexts.get(task_id)

    async def save_context(self, context: A2ATaskContext) -> None:
        """タスクコンテキストを保存.

        Args:
            context: タスクコンテキスト
        """
        async with self._lock:
            self._contexts[context.task_id] = context

    async def update_context_status(
        self,
        task_id: str,
        status: A2ATaskStatus,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> A2ATaskContext | None:
        """タスクコンテキストのステータスを更新.

        Args:
            task_id: タスクID
            status: 新しいステータス
            result: 結果データ（オプション）
            error: エラーメッセージ（オプション）

        Returns:
            更新されたコンテキストまたはNone
        """
        async with self._lock:
            context = self._contexts.get(task_id)
            if context:
                context.status = status
                if result is not None:
                    context.result = result
                if error is not None:
                    context.error = error
            return context

    async def set_conversation_id(
        self, task_id: str, conversation_id: UUID
    ) -> A2ATaskContext | None:
        """タスクにconversation_idを設定.

        Args:
            task_id: タスクID
            conversation_id: 会話ID

        Returns:
            更新されたコンテキストまたはNone
        """
        async with self._lock:
            context = self._contexts.get(task_id)
            if context:
                context.conversation_id = conversation_id
            return context

    async def list_tasks_by_agent(self, agent_id: UUID) -> list[A2ATaskContext]:
        """エージェントのタスク一覧を取得.

        Args:
            agent_id: エージェントID

        Returns:
            タスクコンテキストのリスト
        """
        async with self._lock:
            return [
                ctx for ctx in self._contexts.values() if ctx.agent_id == agent_id
            ]

    async def clear(self) -> None:
        """全てのタスクとコンテキストをクリア."""
        async with self._lock:
            self._tasks.clear()
            self._contexts.clear()


# エージェントIDごとのタスクストアを管理
_agent_task_stores: dict[UUID, TaskStore] = {}
_stores_lock = asyncio.Lock()


async def get_task_store(agent_id: UUID) -> TaskStore:
    """エージェントのタスクストアを取得または作成.

    Args:
        agent_id: エージェントID

    Returns:
        エージェント用のタスクストア
    """
    async with _stores_lock:
        if agent_id not in _agent_task_stores:
            _agent_task_stores[agent_id] = TaskStore()
        return _agent_task_stores[agent_id]


async def clear_all_stores() -> None:
    """全てのタスクストアをクリア（テスト用）."""
    async with _stores_lock:
        for store in _agent_task_stores.values():
            await store.clear()
        _agent_task_stores.clear()

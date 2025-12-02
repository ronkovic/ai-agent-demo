"""A2Aサーバー実装.

既存のChatServiceを使用してA2Aプロトコルを処理する。
"""

import logging
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.chat import ChatService
from ..core.executor import ToolExecutor
from ..db import ConversationRepository, MessageRepository
from ..llm import get_llm_provider
from .task_store import get_task_store
from .types import A2A_SYSTEM_USER_ID, A2ATaskContext, A2ATaskStatus

if TYPE_CHECKING:
    from ..db import Agent

logger = logging.getLogger(__name__)


class A2AServer:
    """A2Aサーバー.

    A2AプロトコルのタスクをChatServiceを使用して処理する。
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize A2A server.

        Args:
            db: Database session for operations.
        """
        self.db = db
        self._chat_service: ChatService | None = None

    def _get_chat_service(self) -> ChatService:
        """Get or create ChatService instance."""
        if self._chat_service is None:
            llm = get_llm_provider()
            self._chat_service = ChatService(
                llm=llm,
                conversation_repo=ConversationRepository(),
                message_repo=MessageRepository(),
                executor=ToolExecutor(),
            )
        return self._chat_service

    async def execute_task(
        self,
        agent: "Agent",
        task_id: str,
        message: str,
    ) -> dict[str, Any]:
        """A2Aタスクを実行する.

        Args:
            agent: タスクを実行するエージェント
            task_id: タスクID
            message: ユーザーメッセージ

        Returns:
            タスク結果
        """
        # タスクストアを取得
        task_store = await get_task_store(agent.id)

        # タスクコンテキストを作成
        context = A2ATaskContext(
            task_id=task_id,
            agent_id=agent.id,
            status=A2ATaskStatus.RUNNING,
        )
        await task_store.save_context(context)

        # タスクデータを保存
        await task_store.save_task(
            task_id,
            {
                "id": task_id,
                "status": "running",
                "agent_id": str(agent.id),
            },
        )

        try:
            # ChatServiceを使用してメッセージを処理
            chat_service = self._get_chat_service()

            conv_id, response = await chat_service.chat(
                db=self.db,
                agent=agent,
                user_id=A2A_SYSTEM_USER_ID,
                user_message=message,
                conversation_id=context.conversation_id,
            )

            # コンテキストを更新
            await task_store.set_conversation_id(task_id, conv_id)
            await task_store.update_context_status(
                task_id,
                A2ATaskStatus.COMPLETED,
                result={"response": response},
            )

            # タスクを完了として保存
            await task_store.save_task(
                task_id,
                {
                    "id": task_id,
                    "status": "completed",
                    "agent_id": str(agent.id),
                    "result": {
                        "message": {
                            "role": "agent",
                            "parts": [{"type": "text", "text": response}],
                        }
                    },
                },
            )

            return {
                "id": task_id,
                "status": "completed",
                "result": {
                    "message": {
                        "role": "agent",
                        "parts": [{"type": "text", "text": response}],
                    }
                },
            }

        except Exception as e:
            logger.exception(f"Task {task_id} execution failed: {e}")

            # エラーステータスを設定
            await task_store.update_context_status(
                task_id,
                A2ATaskStatus.FAILED,
                error=str(e),
            )
            await task_store.save_task(
                task_id,
                {
                    "id": task_id,
                    "status": "failed",
                    "agent_id": str(agent.id),
                    "error": str(e),
                },
            )

            return {
                "id": task_id,
                "status": "failed",
                "error": str(e),
            }

    async def get_task_status(
        self,
        agent: "Agent",
        task_id: str,
    ) -> dict[str, Any] | None:
        """タスクステータスを取得する.

        Args:
            agent: エージェント
            task_id: タスクID

        Returns:
            タスクデータまたはNone
        """
        task_store = await get_task_store(agent.id)
        return await task_store.get_task(task_id)

    async def cancel_task(
        self,
        agent: "Agent",
        task_id: str,
    ) -> dict[str, Any] | None:
        """タスクをキャンセルする.

        Args:
            agent: エージェント
            task_id: タスクID

        Returns:
            更新されたタスクデータまたはNone
        """
        task_store = await get_task_store(agent.id)

        # コンテキストを取得
        context = await task_store.get_context(task_id)
        if not context:
            return None

        # 完了済みタスクはキャンセル不可
        if context.status in (A2ATaskStatus.COMPLETED, A2ATaskStatus.FAILED):
            return await task_store.get_task(task_id)

        # キャンセルステータスを設定
        await task_store.update_context_status(
            task_id,
            A2ATaskStatus.CANCELLED,
        )
        await task_store.save_task(
            task_id,
            {
                "id": task_id,
                "status": "cancelled",
                "agent_id": str(agent.id),
            },
        )

        return {
            "id": task_id,
            "status": "cancelled",
            "agent_id": str(agent.id),
        }


def extract_text_from_message(message: dict[str, Any]) -> str:
    """A2Aメッセージからテキストを抽出する.

    Args:
        message: A2Aメッセージオブジェクト

    Returns:
        抽出されたテキスト
    """
    parts = message.get("parts", [])
    text_parts: list[str] = []

    for part in parts:
        if isinstance(part, dict):
            # TextPart形式
            if part.get("type") == "text" or "text" in part:
                text_parts.append(part.get("text", ""))
        elif isinstance(part, str):
            text_parts.append(part)

    return " ".join(text_parts).strip()

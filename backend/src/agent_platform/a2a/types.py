"""A2A型定義とマッピング."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID


class A2ATaskStatus(str, Enum):
    """A2Aタスクステータス."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class A2ATaskContext:
    """A2Aタスクコンテキスト.

    A2Aプロトコルのタスクと内部会話のマッピングを管理する。
    """

    task_id: str
    agent_id: UUID
    conversation_id: UUID | None = None
    status: A2ATaskStatus = A2ATaskStatus.PENDING
    result: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "agent_id": str(self.agent_id),
            "conversation_id": str(self.conversation_id) if self.conversation_id else None,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
        }


# A2A経由のリクエスト用システムユーザーID
A2A_SYSTEM_USER_ID = UUID("00000000-0000-0000-0000-000000000002")

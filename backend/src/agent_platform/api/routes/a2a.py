"""A2A (Agent-to-Agent) プロトコル API."""

import logging
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...a2a.card import generate_agent_card
from ...a2a.server import A2AServer, extract_text_from_message
from ...db import AgentRepository
from ..deps import get_agent_repo, get_db

logger = logging.getLogger(__name__)

router = APIRouter()


# --- Pydantic Models ---


class AgentCard(BaseModel):
    """A2A Agent Card."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str
    url: str
    version: str = "1.0.0"
    protocol_version: str = Field("0.3.0", alias="protocolVersion")
    capabilities: dict[str, Any] = Field(
        default_factory=lambda: {"streaming": True, "pushNotifications": False}
    )
    skills: list[dict[str, Any]] = Field(default_factory=list)
    default_input_modes: list[str] = Field(
        default_factory=lambda: ["text/plain"], alias="defaultInputModes"
    )
    default_output_modes: list[str] = Field(
        default_factory=lambda: ["text/plain"], alias="defaultOutputModes"
    )
    provider: dict[str, str] | None = None


class MessagePart(BaseModel):
    """A2Aメッセージパート."""

    type: str = "text"
    text: str


class TaskMessage(BaseModel):
    """A2Aタスクメッセージ."""

    role: str = "user"
    parts: list[MessagePart | dict[str, Any]]


class TaskRequest(BaseModel):
    """A2Aタスクリクエスト."""

    id: str | None = None
    message: TaskMessage


class TaskResultMessage(BaseModel):
    """A2Aタスク結果メッセージ."""

    role: str
    parts: list[dict[str, Any]]


class TaskResult(BaseModel):
    """A2Aタスク結果."""

    message: TaskResultMessage | None = None


class TaskResponse(BaseModel):
    """A2Aタスクレスポンス."""

    id: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    result: TaskResult | None = None
    error: str | None = None
    agent_id: str | None = None


# --- Helper Functions ---


async def get_a2a_enabled_agent(
    agent_id: UUID,
    db: AsyncSession,
    agent_repo: AgentRepository,
):
    """A2A有効なエージェントを取得.

    Args:
        agent_id: Agent UUID.
        db: Database session.
        agent_repo: Agent repository.

    Returns:
        Agent instance.

    Raises:
        HTTPException: If agent not found or A2A not enabled.
    """
    agent = await agent_repo.get(db, agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if not agent.a2a_enabled:
        raise HTTPException(
            status_code=403,
            detail="A2A is not enabled for this agent",
        )

    return agent


# --- Endpoints ---


@router.get("/agents/{agent_id}/.well-known/agent.json", response_model=AgentCard)
async def get_agent_card(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    agent_repo: AgentRepository = Depends(get_agent_repo),
) -> dict[str, Any]:
    """Agent Card取得.

    A2Aプロトコルの発見メカニズム用エンドポイント。
    エージェントの機能とスキルを記述したAgent Cardを返す。
    """
    agent = await get_a2a_enabled_agent(agent_id, db, agent_repo)
    return generate_agent_card(agent)


@router.post("/agents/{agent_id}/tasks", response_model=TaskResponse)
async def create_task(
    agent_id: UUID,
    task: TaskRequest,
    db: AsyncSession = Depends(get_db),
    agent_repo: AgentRepository = Depends(get_agent_repo),
) -> dict[str, Any]:
    """タスク送信.

    A2Aプロトコルでタスクを送信し、エージェントに処理を依頼する。
    """
    agent = await get_a2a_enabled_agent(agent_id, db, agent_repo)

    # タスクIDを生成または使用
    task_id = task.id or str(uuid4())

    # メッセージからテキストを抽出
    message_dict = task.message.model_dump()
    user_message = extract_text_from_message(message_dict)

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Message must contain text content",
        )

    # A2Aサーバーでタスクを実行
    server = A2AServer(db)
    result = await server.execute_task(agent, task_id, user_message)

    return result


@router.get("/agents/{agent_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    agent_id: UUID,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    agent_repo: AgentRepository = Depends(get_agent_repo),
) -> dict[str, Any]:
    """タスク状態取得.

    送信したタスクの現在の状態を取得する。
    """
    agent = await get_a2a_enabled_agent(agent_id, db, agent_repo)

    server = A2AServer(db)
    result = await server.get_task_status(agent, task_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return result


@router.post("/agents/{agent_id}/tasks/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(
    agent_id: UUID,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    agent_repo: AgentRepository = Depends(get_agent_repo),
) -> dict[str, Any]:
    """タスクキャンセル.

    実行中のタスクをキャンセルする。
    """
    agent = await get_a2a_enabled_agent(agent_id, db, agent_repo)

    server = A2AServer(db)
    result = await server.cancel_task(agent, task_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return result

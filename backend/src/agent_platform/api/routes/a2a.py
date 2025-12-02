"""A2A (Agent-to-Agent) プロトコル API."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AgentCard(BaseModel):
    """A2A Agent Card."""

    name: str
    description: str
    url: str
    version: str = "1.0.0"
    capabilities: dict = {"streaming": True, "pushNotifications": False}
    skills: list[dict] = []


class TaskRequest(BaseModel):
    """A2Aタスクリクエスト."""

    id: str
    message: dict


class TaskResponse(BaseModel):
    """A2Aタスクレスポンス."""

    id: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    result: dict | None = None


@router.get("/agents/{agent_id}/.well-known/agent.json")
async def get_agent_card(agent_id: UUID) -> AgentCard:
    """Agent Card取得."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/agents/{agent_id}/tasks")
async def create_task(agent_id: UUID, task: TaskRequest) -> TaskResponse:
    """タスク送信."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/agents/{agent_id}/tasks/{task_id}")
async def get_task(agent_id: UUID, task_id: str) -> TaskResponse:
    """タスク状態取得."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/agents/{agent_id}/tasks/{task_id}/cancel")
async def cancel_task(agent_id: UUID, task_id: str) -> TaskResponse:
    """タスクキャンセル."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")

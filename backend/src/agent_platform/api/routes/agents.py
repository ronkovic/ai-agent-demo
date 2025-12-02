"""エージェント管理API."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AgentCreate(BaseModel):
    """エージェント作成リクエスト."""

    name: str
    description: str | None = None
    system_prompt: str
    llm_provider: str  # 'claude', 'openai', 'bedrock'
    llm_model: str
    tools: list[str] = []
    a2a_enabled: bool = False


class AgentResponse(BaseModel):
    """エージェントレスポンス."""

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    system_prompt: str
    llm_provider: str
    llm_model: str
    tools: list[str]
    a2a_enabled: bool


class AgentUpdate(BaseModel):
    """エージェント更新リクエスト."""

    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    tools: list[str] | None = None
    a2a_enabled: bool | None = None


@router.get("")
async def list_agents() -> list[AgentResponse]:
    """エージェント一覧取得."""
    # TODO: 実装
    return []


@router.post("")
async def create_agent(agent: AgentCreate) -> AgentResponse:
    """エージェント作成."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{agent_id}")
async def get_agent(agent_id: UUID) -> AgentResponse:
    """エージェント取得."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/{agent_id}")
async def update_agent(agent_id: UUID, agent: AgentUpdate) -> AgentResponse:
    """エージェント更新."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{agent_id}")
async def delete_agent(agent_id: UUID) -> dict[str, str]:
    """エージェント削除."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")

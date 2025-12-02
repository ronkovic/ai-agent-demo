"""エージェント管理API."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import AgentRepository
from ..deps import get_agent_repo, get_current_user_id, get_db

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================


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

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    system_prompt: str
    llm_provider: str
    llm_model: str
    tools: list[str]
    a2a_enabled: bool
    created_at: datetime
    updated_at: datetime


class AgentUpdate(BaseModel):
    """エージェント更新リクエスト."""

    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    tools: list[str] | None = None
    a2a_enabled: bool | None = None


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: AgentRepository = Depends(get_agent_repo),
) -> list[AgentResponse]:
    """エージェント一覧取得."""
    agents = await repo.list_by_user(db, user_id)
    return [AgentResponse.model_validate(agent) for agent in agents]


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: AgentRepository = Depends(get_agent_repo),
) -> AgentResponse:
    """エージェント作成."""
    agent = await repo.create(
        db,
        user_id=user_id,
        name=agent_data.name,
        description=agent_data.description,
        system_prompt=agent_data.system_prompt,
        llm_provider=agent_data.llm_provider,
        llm_model=agent_data.llm_model,
        tools=agent_data.tools,
        a2a_enabled=agent_data.a2a_enabled,
    )
    return AgentResponse.model_validate(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: AgentRepository = Depends(get_agent_repo),
) -> AgentResponse:
    """エージェント取得."""
    agent = await repo.get_by_user(db, agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    return AgentResponse.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: AgentRepository = Depends(get_agent_repo),
) -> AgentResponse:
    """エージェント更新."""
    agent = await repo.get_by_user(db, agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    # Only update fields that were provided
    update_data = agent_data.model_dump(exclude_unset=True)
    agent = await repo.update(db, agent, **update_data)
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: AgentRepository = Depends(get_agent_repo),
) -> None:
    """エージェント削除."""
    agent = await repo.get_by_user(db, agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    await repo.delete(db, agent)

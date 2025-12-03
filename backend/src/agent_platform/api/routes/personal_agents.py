"""Personal Agent管理API."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import PersonalAgentRepository
from ..deps import get_current_user_id, get_db, get_personal_agent_repo

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================


class PersonalAgentCreate(BaseModel):
    """Personal Agent作成リクエスト."""

    name: str
    description: str | None = None
    system_prompt: str
    is_public: bool = False


class PersonalAgentResponse(BaseModel):
    """Personal Agentレスポンス."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    system_prompt: str
    is_public: bool
    created_at: datetime
    updated_at: datetime


class PersonalAgentUpdate(BaseModel):
    """Personal Agent更新リクエスト."""

    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    is_public: bool | None = None


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("", response_model=list[PersonalAgentResponse])
async def list_personal_agents(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: PersonalAgentRepository = Depends(get_personal_agent_repo),
) -> list[PersonalAgentResponse]:
    """Personal Agent一覧取得."""
    agents = await repo.list_by_user(db, user_id)
    return [PersonalAgentResponse.model_validate(agent) for agent in agents]


@router.post("", response_model=PersonalAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_personal_agent(
    agent_data: PersonalAgentCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: PersonalAgentRepository = Depends(get_personal_agent_repo),
) -> PersonalAgentResponse:
    """Personal Agent作成."""
    agent = await repo.create(
        db,
        user_id=user_id,
        name=agent_data.name,
        description=agent_data.description,
        system_prompt=agent_data.system_prompt,
        is_public=agent_data.is_public,
    )
    return PersonalAgentResponse.model_validate(agent)


@router.get("/{agent_id}", response_model=PersonalAgentResponse)
async def get_personal_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: PersonalAgentRepository = Depends(get_personal_agent_repo),
) -> PersonalAgentResponse:
    """Personal Agent取得."""
    agent = await repo.get_by_user(db, agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal Agent {agent_id} not found",
        )
    return PersonalAgentResponse.model_validate(agent)


@router.patch("/{agent_id}", response_model=PersonalAgentResponse)
async def update_personal_agent(
    agent_id: UUID,
    agent_data: PersonalAgentUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: PersonalAgentRepository = Depends(get_personal_agent_repo),
) -> PersonalAgentResponse:
    """Personal Agent更新."""
    agent = await repo.get_by_user(db, agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal Agent {agent_id} not found",
        )

    # Only update fields that were provided
    update_data = agent_data.model_dump(exclude_unset=True)
    agent = await repo.update(db, agent, **update_data)
    return PersonalAgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_personal_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: PersonalAgentRepository = Depends(get_personal_agent_repo),
) -> None:
    """Personal Agent削除."""
    agent = await repo.get_by_user(db, agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal Agent {agent_id} not found",
        )
    await repo.delete(db, agent)

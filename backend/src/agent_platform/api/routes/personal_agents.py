"""Personal Agent管理API."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from ...core.chat import ChatService
from ...db import (
    ConversationRepository,
    MessageRepository,
    PersonalAgentRepository,
    UserLLMConfigRepository,
)
from ...llm import get_llm_provider
from ..deps import (
    get_conversation_repo,
    get_current_user_id,
    get_db,
    get_message_repo,
    get_personal_agent_repo,
    get_user_llm_config_repo,
)

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


# =============================================================================
# Chat Endpoints
# =============================================================================


# Default models for each provider
DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o-mini",
    "google": "gemini-2.0-flash-exp",
    "bedrock": "anthropic.claude-3-5-sonnet-20241022-v2:0",
}


@dataclass
class PersonalAgentAdapter:
    """Adapter to make PersonalAgent compatible with ChatService."""

    id: UUID
    system_prompt: str
    llm_model: str
    tools: list[Any] = field(default_factory=list)


class PersonalAgentChatRequest(BaseModel):
    """Personal Agentチャットリクエスト."""

    conversation_id: UUID | None = None
    message: str


def get_chat_service(
    conversation_repo: ConversationRepository = Depends(get_conversation_repo),
    message_repo: MessageRepository = Depends(get_message_repo),
) -> ChatService:
    """Get chat service instance."""
    llm = get_llm_provider()
    return ChatService(llm, conversation_repo, message_repo)


@router.post("/{agent_id}/chat/stream")
async def personal_agent_chat_stream(
    agent_id: UUID,
    request: PersonalAgentChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: PersonalAgentRepository = Depends(get_personal_agent_repo),
    llm_config_repo: UserLLMConfigRepository = Depends(get_user_llm_config_repo),
    chat_service: ChatService = Depends(get_chat_service),
) -> EventSourceResponse:
    """Personal Agentとのチャット（SSEストリーミング）."""
    # Get personal agent
    personal_agent = await repo.get_by_user(db, agent_id, user_id)
    if not personal_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal Agent {agent_id} not found",
        )

    # Get user's default LLM config
    llm_config = await llm_config_repo.get_default_by_user(db, user_id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LLM APIキーが設定されていません。設定画面からAPIキーを追加してください。",
        )

    # Get default model for the provider
    llm_model = DEFAULT_MODELS.get(llm_config.provider, "gpt-4o-mini")

    # Create adapter for ChatService
    agent_adapter = PersonalAgentAdapter(
        id=personal_agent.id,
        system_prompt=personal_agent.system_prompt,
        llm_model=llm_model,
        tools=[],  # Personal agents don't have tools yet
    )

    # Start streaming chat
    conversation_id, stream = await chat_service.chat_stream(
        db=db,
        agent=agent_adapter,  # type: ignore[arg-type]
        user_id=user_id,
        user_message=request.message,
        conversation_id=request.conversation_id,
    )

    async def event_generator():
        """Generate SSE events."""
        # First, send conversation_id
        yield {
            "event": "start",
            "data": f'{{"conversation_id": "{conversation_id}"}}',
        }

        # Stream content chunks
        async for chunk in stream:
            yield {
                "event": "content",
                "data": chunk,
            }

        # Signal completion
        yield {
            "event": "done",
            "data": "{}",
        }

    return EventSourceResponse(event_generator())

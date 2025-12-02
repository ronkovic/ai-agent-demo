"""チャットAPI."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from ..deps import (
    get_conversation_repo,
    get_current_user_id,
    get_db,
    get_message_repo,
)
from ...core.chat import ChatService
from ...db import AgentRepository, Conversation, ConversationRepository, MessageRepository
from ...llm import get_llm_provider

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================


class ChatMessageResponse(BaseModel):
    """チャットメッセージ."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str  # 'user', 'assistant', 'tool'
    content: str
    created_at: datetime


class ChatRequest(BaseModel):
    """チャットリクエスト."""

    agent_id: UUID
    conversation_id: UUID | None = None
    message: str


class ChatResponse(BaseModel):
    """チャットレスポンス."""

    conversation_id: UUID
    message: ChatMessageResponse


class ConversationResponse(BaseModel):
    """会話レスポンス."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agent_id: UUID
    user_id: UUID
    title: str | None
    created_at: datetime


class ConversationWithMessagesResponse(ConversationResponse):
    """会話とメッセージのレスポンス."""

    messages: list[ChatMessageResponse]


# =============================================================================
# Dependencies
# =============================================================================


def get_chat_service(
    conversation_repo: ConversationRepository = Depends(get_conversation_repo),
    message_repo: MessageRepository = Depends(get_message_repo),
) -> ChatService:
    """Get chat service instance."""
    llm = get_llm_provider()
    return ChatService(llm, conversation_repo, message_repo)


def get_agent_repo() -> AgentRepository:
    """Get agent repository instance."""
    return AgentRepository()


# =============================================================================
# Helper Functions
# =============================================================================


async def get_agent_or_404(
    db: AsyncSession,
    agent_id: UUID,
    user_id: UUID,
    repo: AgentRepository,
) -> object:
    """Get agent or raise 404."""
    agent = await repo.get_by_user(db, agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    return agent


# =============================================================================
# Chat Endpoints
# =============================================================================


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service),
    agent_repo: AgentRepository = Depends(get_agent_repo),
) -> ChatResponse:
    """チャットメッセージ送信（非ストリーミング）."""
    # Get agent
    agent = await get_agent_or_404(db, request.agent_id, user_id, agent_repo)

    # Process chat
    conversation_id, response_content = await chat_service.chat(
        db=db,
        agent=agent,
        user_id=user_id,
        user_message=request.message,
        conversation_id=request.conversation_id,
    )

    # Get the saved message for response
    message_repo = MessageRepository()
    messages = await message_repo.list_by_conversation(db, conversation_id)
    last_message = messages[-1]  # Get the assistant's response

    return ChatResponse(
        conversation_id=conversation_id,
        message=ChatMessageResponse.model_validate(last_message),
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service),
    agent_repo: AgentRepository = Depends(get_agent_repo),
) -> EventSourceResponse:
    """チャットメッセージ送信（SSEストリーミング）."""
    # Get agent
    agent = await get_agent_or_404(db, request.agent_id, user_id, agent_repo)

    # Start streaming chat
    conversation_id, stream = await chat_service.chat_stream(
        db=db,
        agent=agent,
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


# =============================================================================
# Conversation Endpoints
# =============================================================================


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    conversation_repo: ConversationRepository = Depends(get_conversation_repo),
) -> list[ConversationResponse]:
    """会話一覧取得."""
    conversations = await conversation_repo.list_by_agent(db, agent_id, user_id)
    return [ConversationResponse.model_validate(conv) for conv in conversations]


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    agent_id: UUID,
    title: str | None = None,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    conversation_repo: ConversationRepository = Depends(get_conversation_repo),
    agent_repo: AgentRepository = Depends(get_agent_repo),
) -> ConversationResponse:
    """会話作成."""
    # Verify agent exists
    await get_agent_or_404(db, agent_id, user_id, agent_repo)

    conversation = await conversation_repo.create(
        db,
        agent_id=agent_id,
        user_id=user_id,
        title=title,
    )
    return ConversationResponse.model_validate(conversation)


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationWithMessagesResponse,
)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    conversation_repo: ConversationRepository = Depends(get_conversation_repo),
    message_repo: MessageRepository = Depends(get_message_repo),
) -> ConversationWithMessagesResponse:
    """会話履歴取得."""
    conversation = await conversation_repo.get(db, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found",
        )

    messages = await message_repo.list_by_conversation(db, conversation_id)

    return ConversationWithMessagesResponse(
        id=conversation.id,
        agent_id=conversation.agent_id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=[ChatMessageResponse.model_validate(msg) for msg in messages],
    )


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    conversation_repo: ConversationRepository = Depends(get_conversation_repo),
) -> None:
    """会話削除."""
    conversation = await conversation_repo.get(db, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found",
        )
    await conversation_repo.delete(db, conversation)

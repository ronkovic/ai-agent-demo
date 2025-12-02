"""チャットAPI."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


class ChatMessage(BaseModel):
    """チャットメッセージ."""

    role: str  # 'user', 'assistant', 'tool'
    content: str


class ChatRequest(BaseModel):
    """チャットリクエスト."""

    agent_id: UUID
    conversation_id: UUID | None = None
    message: str


class ChatResponse(BaseModel):
    """チャットレスポンス."""

    conversation_id: UUID
    message: ChatMessage
    tool_calls: list[dict] | None = None


@router.post("")
async def chat(request: ChatRequest) -> ChatResponse:
    """チャットメッセージ送信（非ストリーミング）."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """チャットメッセージ送信（SSEストリーミング）."""

    async def generate():
        # TODO: 実装
        yield "data: {\"error\": \"Not implemented\"}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: UUID) -> dict:
    """会話履歴取得."""
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/conversations")
async def list_conversations(agent_id: UUID | None = None) -> list[dict]:
    """会話一覧取得."""
    # TODO: 実装
    return []

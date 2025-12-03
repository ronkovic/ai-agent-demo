"""API dependencies for dependency injection."""

import hashlib
from datetime import UTC, datetime
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.jwt import AuthError, extract_user_id, verify_supabase_token
from ..core.config import settings
from ..db import (
    AgentRepository,
    ConversationRepository,
    MessageRepository,
    PersonalAgentRepository,
    UserApiKey,
    UserApiKeyRepository,
    UserLLMConfigRepository,
    WorkflowExecutionRepository,
    WorkflowRepository,
)
from ..db.session import get_db
from ..services.rate_limiter import get_rate_limit_key, rate_limiter

# Re-export get_db for convenience
__all__ = [
    "get_db",
    "get_agent_repo",
    "get_conversation_repo",
    "get_message_repo",
    "get_personal_agent_repo",
    "get_user_llm_config_repo",
    "get_user_api_key_repo",
    "get_workflow_repo",
    "get_workflow_execution_repo",
    "get_current_user_id",
    "verify_api_key",
]

# HTTP Bearer token security scheme
# auto_error=False allows us to handle missing tokens ourselves
security = HTTPBearer(auto_error=False)


def get_agent_repo() -> AgentRepository:
    """Get agent repository instance."""
    return AgentRepository()


def get_conversation_repo() -> ConversationRepository:
    """Get conversation repository instance."""
    return ConversationRepository()


def get_message_repo() -> MessageRepository:
    """Get message repository instance."""
    return MessageRepository()


def get_personal_agent_repo() -> PersonalAgentRepository:
    """Get personal agent repository instance."""
    return PersonalAgentRepository()


def get_user_llm_config_repo() -> UserLLMConfigRepository:
    """Get user LLM config repository instance."""
    return UserLLMConfigRepository()


def get_user_api_key_repo() -> UserApiKeyRepository:
    """Get user API key repository instance."""
    return UserApiKeyRepository()


def get_workflow_repo() -> WorkflowRepository:
    """Get workflow repository instance."""
    return WorkflowRepository()


def get_workflow_execution_repo() -> WorkflowExecutionRepository:
    """Get workflow execution repository instance."""
    return WorkflowExecutionRepository()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UUID:
    """Get current user ID from JWT token.

    In debug mode without credentials, returns a development user ID.
    In production, verifies the Supabase JWT and extracts the user ID.

    Args:
        credentials: The HTTP Bearer credentials from the request.

    Returns:
        The authenticated user's ID.

    Raises:
        HTTPException: If authentication fails.
    """
    # Debug mode: allow requests without authentication
    if settings.debug and credentials is None:
        return UUID("00000000-0000-0000-0000-000000000001")

    # Production mode: require authentication
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_supabase_token(credentials.credentials)
        return extract_user_id(payload)
    except AuthError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> UserApiKey:
    """APIキー認証 + Rate Limiting.

    Args:
        x_api_key: X-API-Key ヘッダー値
        db: データベースセッション

    Returns:
        認証されたUserApiKeyインスタンス

    Raises:
        HTTPException: 認証失敗、有効期限切れ、レート制限超過
    """
    # ハッシュ計算
    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()

    # APIキー検索
    api_key_repo = UserApiKeyRepository()
    api_key = await api_key_repo.get_by_hash(db, key_hash)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # 有効期限チェック
    if api_key.expires_at and api_key.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired",
        )

    # Rate Limiting
    rate_key = get_rate_limit_key(api_key.id)
    allowed, remaining = await rate_limiter.check_rate_limit(
        rate_key,
        api_key.rate_limit,
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"X-RateLimit-Remaining": "0"},
        )

    # last_used_at 更新
    api_key.last_used_at = datetime.now(UTC)

    return api_key

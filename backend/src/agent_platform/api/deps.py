"""API dependencies for dependency injection."""

from uuid import UUID

from ..db import AgentRepository, ConversationRepository, MessageRepository
from ..db.session import get_db

# Re-export get_db for convenience
__all__ = [
    "get_db",
    "get_agent_repo",
    "get_conversation_repo",
    "get_message_repo",
    "get_current_user_id",
]


def get_agent_repo() -> AgentRepository:
    """Get agent repository instance."""
    return AgentRepository()


def get_conversation_repo() -> ConversationRepository:
    """Get conversation repository instance."""
    return ConversationRepository()


def get_message_repo() -> MessageRepository:
    """Get message repository instance."""
    return MessageRepository()


async def get_current_user_id() -> UUID:
    """Get current user ID.

    NOTE: This is a placeholder for development.
    In production, this should verify Supabase JWT and extract user_id.
    """
    # Development user ID
    return UUID("00000000-0000-0000-0000-000000000001")

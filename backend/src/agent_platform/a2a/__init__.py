"""A2A (Agent-to-Agent) protocol module."""

from .card import generate_agent_card, generate_agent_card_json
from .client import A2AClient, A2AClientError, get_a2a_client
from .server import A2AServer, extract_text_from_message
from .task_store import TaskStore, clear_all_stores, get_task_store
from .types import A2A_SYSTEM_USER_ID, A2ATaskContext, A2ATaskStatus

__all__ = [
    # Types
    "A2ATaskStatus",
    "A2ATaskContext",
    "A2A_SYSTEM_USER_ID",
    # Card generation
    "generate_agent_card",
    "generate_agent_card_json",
    # Task store
    "TaskStore",
    "get_task_store",
    "clear_all_stores",
    # Server
    "A2AServer",
    "extract_text_from_message",
    # Client
    "A2AClient",
    "A2AClientError",
    "get_a2a_client",
]

"""Chat service for handling conversations with agents."""

from collections.abc import AsyncIterator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..db import Agent, ConversationRepository, MessageRepository
from ..llm import ChatMessage as LLMChatMessage
from ..llm import LLMProvider


class ChatService:
    """Service for handling chat conversations with agents."""

    def __init__(
        self,
        llm: LLMProvider,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
    ):
        """Initialize chat service.

        Args:
            llm: LLM provider for generating responses.
            conversation_repo: Repository for conversation data.
            message_repo: Repository for message data.
        """
        self.llm = llm
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo

    async def _get_or_create_conversation(
        self,
        db: AsyncSession,
        agent: Agent,
        user_id: UUID,
        conversation_id: UUID | None,
    ) -> UUID:
        """Get existing conversation or create a new one.

        Args:
            db: Database session.
            agent: Agent for the conversation.
            user_id: User ID.
            conversation_id: Optional existing conversation ID.

        Returns:
            Conversation ID.
        """
        if conversation_id:
            conversation = await self.conversation_repo.get(db, conversation_id)
            if conversation:
                return conversation.id

        # Create new conversation
        conversation = await self.conversation_repo.create(
            db,
            agent_id=agent.id,
            user_id=user_id,
        )
        return conversation.id

    async def _build_messages(
        self,
        db: AsyncSession,
        agent: Agent,
        conversation_id: UUID,
        user_message: str,
    ) -> list[LLMChatMessage]:
        """Build message list for LLM including history.

        Args:
            db: Database session.
            agent: Agent with system prompt.
            conversation_id: Conversation ID for history.
            user_message: New user message.

        Returns:
            List of chat messages for LLM.
        """
        messages: list[LLMChatMessage] = []

        # Add system prompt
        messages.append(LLMChatMessage(role="system", content=agent.system_prompt))

        # Add conversation history
        history = await self.message_repo.list_by_conversation(db, conversation_id)
        for msg in history:
            messages.append(LLMChatMessage(role=msg.role, content=msg.content))

        # Add new user message
        messages.append(LLMChatMessage(role="user", content=user_message))

        return messages

    async def chat(
        self,
        db: AsyncSession,
        agent: Agent,
        user_id: UUID,
        user_message: str,
        conversation_id: UUID | None = None,
    ) -> tuple[UUID, str]:
        """Handle a chat message (non-streaming).

        Args:
            db: Database session.
            agent: Agent to chat with.
            user_id: User ID.
            user_message: User's message.
            conversation_id: Optional existing conversation ID.

        Returns:
            Tuple of (conversation_id, assistant_response).
        """
        # Get or create conversation
        conv_id = await self._get_or_create_conversation(
            db, agent, user_id, conversation_id
        )

        # Save user message
        await self.message_repo.create(
            db,
            conversation_id=conv_id,
            role="user",
            content=user_message,
        )

        # Build messages for LLM
        messages = await self._build_messages(db, agent, conv_id, user_message)

        # Get LLM response
        response = await self.llm.chat(
            messages=messages,
            model=agent.llm_model,
        )

        # Save assistant message
        await self.message_repo.create(
            db,
            conversation_id=conv_id,
            role="assistant",
            content=response.content,
        )

        return conv_id, response.content

    async def chat_stream(
        self,
        db: AsyncSession,
        agent: Agent,
        user_id: UUID,
        user_message: str,
        conversation_id: UUID | None = None,
    ) -> tuple[UUID, AsyncIterator[str]]:
        """Handle a streaming chat message.

        Args:
            db: Database session.
            agent: Agent to chat with.
            user_id: User ID.
            user_message: User's message.
            conversation_id: Optional existing conversation ID.

        Returns:
            Tuple of (conversation_id, async iterator of response chunks).
        """
        # Get or create conversation
        conv_id = await self._get_or_create_conversation(
            db, agent, user_id, conversation_id
        )

        # Save user message
        await self.message_repo.create(
            db,
            conversation_id=conv_id,
            role="user",
            content=user_message,
        )

        # Build messages for LLM (excluding the new user message since we already saved it)
        messages = await self._build_messages(db, agent, conv_id, user_message)

        async def stream_and_save() -> AsyncIterator[str]:
            """Stream response and save when complete."""
            full_response: list[str] = []

            async for chunk in self.llm.chat_stream(
                messages=messages,
                model=agent.llm_model,
            ):
                full_response.append(chunk)
                yield chunk

            # Save complete assistant message
            complete_content = "".join(full_response)
            await self.message_repo.create(
                db,
                conversation_id=conv_id,
                role="assistant",
                content=complete_content,
            )

        return conv_id, stream_and_save()

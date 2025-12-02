"""Repository pattern for data access."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Agent, AgentCard, Conversation, Message


# =============================================================================
# Agent Repository
# =============================================================================


class AgentRepository:
    """Agent data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        name: str,
        system_prompt: str,
        llm_provider: str,
        llm_model: str,
        description: str | None = None,
        tools: list[str] | None = None,
        a2a_enabled: bool = False,
    ) -> Agent:
        """Create a new agent."""
        agent = Agent(
            user_id=user_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tools=tools or [],
            a2a_enabled=a2a_enabled,
        )
        db.add(agent)
        await db.flush()
        await db.refresh(agent)
        return agent

    async def get(self, db: AsyncSession, agent_id: UUID) -> Agent | None:
        """Get agent by ID."""
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, db: AsyncSession, agent_id: UUID, user_id: UUID) -> Agent | None:
        """Get agent by ID and user ID."""
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, db: AsyncSession, user_id: UUID) -> list[Agent]:
        """List all agents for a user."""
        result = await db.execute(
            select(Agent).where(Agent.user_id == user_id).order_by(Agent.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        agent: Agent,
        **kwargs: str | bool | list[str] | None,
    ) -> Agent:
        """Update agent fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(agent, key):
                setattr(agent, key, value)
        await db.flush()
        await db.refresh(agent)
        return agent

    async def delete(self, db: AsyncSession, agent: Agent) -> None:
        """Delete an agent."""
        await db.delete(agent)
        await db.flush()


# =============================================================================
# Conversation Repository
# =============================================================================


class ConversationRepository:
    """Conversation data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        agent_id: UUID,
        user_id: UUID,
        title: str | None = None,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            agent_id=agent_id,
            user_id=user_id,
            title=title,
        )
        db.add(conversation)
        await db.flush()
        await db.refresh(conversation)
        return conversation

    async def get(self, db: AsyncSession, conversation_id: UUID) -> Conversation | None:
        """Get conversation by ID."""
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_with_messages(
        self, db: AsyncSession, conversation_id: UUID
    ) -> Conversation | None:
        """Get conversation by ID with messages."""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def list_by_agent(
        self, db: AsyncSession, agent_id: UUID, user_id: UUID
    ) -> list[Conversation]:
        """List all conversations for an agent."""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.agent_id == agent_id, Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_title(
        self, db: AsyncSession, conversation: Conversation, title: str
    ) -> Conversation:
        """Update conversation title."""
        conversation.title = title
        await db.flush()
        await db.refresh(conversation)
        return conversation

    async def delete(self, db: AsyncSession, conversation: Conversation) -> None:
        """Delete a conversation."""
        await db.delete(conversation)
        await db.flush()


# =============================================================================
# Message Repository
# =============================================================================


class MessageRepository:
    """Message data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        conversation_id: UUID,
        role: str,
        content: str,
        tool_calls: dict | None = None,
        a2a_source: UUID | None = None,
    ) -> Message:
        """Create a new message."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            a2a_source=a2a_source,
        )
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message

    async def list_by_conversation(
        self, db: AsyncSession, conversation_id: UUID
    ) -> list[Message]:
        """List all messages for a conversation."""
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())


# =============================================================================
# AgentCard Repository
# =============================================================================


class AgentCardRepository:
    """AgentCard data access repository."""

    async def create_or_update(
        self,
        db: AsyncSession,
        *,
        agent_id: UUID,
        card_json: dict,
        endpoint_url: str | None = None,
    ) -> AgentCard:
        """Create or update agent card."""
        result = await db.execute(
            select(AgentCard).where(AgentCard.agent_id == agent_id)
        )
        agent_card = result.scalar_one_or_none()

        if agent_card:
            agent_card.card_json = card_json
            agent_card.endpoint_url = endpoint_url
        else:
            agent_card = AgentCard(
                agent_id=agent_id,
                card_json=card_json,
                endpoint_url=endpoint_url,
            )
            db.add(agent_card)

        await db.flush()
        await db.refresh(agent_card)
        return agent_card

    async def get_by_agent(self, db: AsyncSession, agent_id: UUID) -> AgentCard | None:
        """Get agent card by agent ID."""
        result = await db.execute(
            select(AgentCard).where(AgentCard.agent_id == agent_id)
        )
        return result.scalar_one_or_none()

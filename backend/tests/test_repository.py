"""Repository layer tests."""

from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db import AgentRepository, ConversationRepository, MessageRepository


class TestAgentRepository:
    """Tests for AgentRepository."""

    @pytest.mark.asyncio
    async def test_create_agent(self, db_session: AsyncSession, test_user_id: UUID):
        """Test creating an agent."""
        repo = AgentRepository()

        agent = await repo.create(
            db_session,
            user_id=test_user_id,
            name="Test Agent",
            description="Test description",
            system_prompt="You are a test assistant.",
            llm_provider="claude",
            llm_model="claude-3-5-sonnet-20241022",
            tools=["search", "calculator"],
            a2a_enabled=True,
        )

        assert agent.id is not None
        assert agent.user_id == test_user_id
        assert agent.name == "Test Agent"
        assert agent.description == "Test description"
        assert agent.llm_provider == "claude"
        assert agent.tools == ["search", "calculator"]
        assert agent.a2a_enabled is True

    @pytest.mark.asyncio
    async def test_get_agent(self, db_session: AsyncSession, test_user_id: UUID):
        """Test getting an agent by ID."""
        repo = AgentRepository()

        # Create agent
        agent = await repo.create(
            db_session,
            user_id=test_user_id,
            name="Get Test Agent",
            system_prompt="Test prompt",
            llm_provider="openai",
            llm_model="gpt-4o",
        )
        await db_session.flush()

        # Get agent
        retrieved = await repo.get(db_session, agent.id)
        assert retrieved is not None
        assert retrieved.id == agent.id
        assert retrieved.name == "Get Test Agent"

    @pytest.mark.asyncio
    async def test_get_nonexistent_agent(self, db_session: AsyncSession):
        """Test getting a non-existent agent."""
        repo = AgentRepository()
        result = await repo.get(
            db_session, UUID("00000000-0000-0000-0000-000000000999")
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_list_agents_by_user(self, db_session: AsyncSession, test_user_id: UUID):
        """Test listing agents for a user."""
        repo = AgentRepository()

        # Create multiple agents
        for i in range(3):
            await repo.create(
                db_session,
                user_id=test_user_id,
                name=f"Agent {i}",
                system_prompt=f"Prompt {i}",
                llm_provider="claude",
                llm_model="claude-3-5-sonnet-20241022",
            )
        await db_session.flush()

        # List agents
        agents = await repo.list_by_user(db_session, test_user_id)
        assert len(agents) >= 3

    @pytest.mark.asyncio
    async def test_update_agent(self, db_session: AsyncSession, test_user_id: UUID):
        """Test updating an agent."""
        repo = AgentRepository()

        # Create agent
        agent = await repo.create(
            db_session,
            user_id=test_user_id,
            name="Original Name",
            system_prompt="Original prompt",
            llm_provider="claude",
            llm_model="claude-3-5-sonnet-20241022",
        )

        # Update agent
        updated = await repo.update(
            db_session,
            agent,
            name="Updated Name",
            description="New description",
        )

        assert updated.name == "Updated Name"
        assert updated.description == "New description"
        assert updated.system_prompt == "Original prompt"  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_agent(self, db_session: AsyncSession, test_user_id: UUID):
        """Test deleting an agent."""
        repo = AgentRepository()

        # Create agent
        agent = await repo.create(
            db_session,
            user_id=test_user_id,
            name="Delete Test",
            system_prompt="Test",
            llm_provider="claude",
            llm_model="claude-3-5-sonnet-20241022",
        )
        await db_session.flush()
        agent_id = agent.id

        # Delete agent
        await repo.delete(db_session, agent)
        await db_session.flush()

        # Verify deleted
        result = await repo.get(db_session, agent_id)
        assert result is None


class TestConversationRepository:
    """Tests for ConversationRepository."""

    @pytest.mark.asyncio
    async def test_create_conversation(
        self, db_session: AsyncSession, sample_agent: dict, test_user_id: UUID
    ):
        """Test creating a conversation."""
        repo = ConversationRepository()

        conversation = await repo.create(
            db_session,
            agent_id=UUID(sample_agent["id"]),
            user_id=test_user_id,
            title="Test Conversation",
        )

        assert conversation.id is not None
        assert conversation.agent_id == UUID(sample_agent["id"])
        assert conversation.title == "Test Conversation"

    @pytest.mark.asyncio
    async def test_list_conversations_by_agent(
        self, db_session: AsyncSession, sample_agent: dict, test_user_id: UUID
    ):
        """Test listing conversations for an agent."""
        repo = ConversationRepository()

        # Create conversations
        for i in range(2):
            await repo.create(
                db_session,
                agent_id=UUID(sample_agent["id"]),
                user_id=test_user_id,
                title=f"Conversation {i}",
            )
        await db_session.flush()

        # List conversations
        conversations = await repo.list_by_agent(
            db_session, UUID(sample_agent["id"]), test_user_id
        )
        assert len(conversations) >= 2


class TestMessageRepository:
    """Tests for MessageRepository."""

    @pytest.mark.asyncio
    async def test_create_message(
        self, db_session: AsyncSession, sample_agent: dict, test_user_id: UUID
    ):
        """Test creating a message."""
        conv_repo = ConversationRepository()
        msg_repo = MessageRepository()

        # Create conversation first
        conversation = await conv_repo.create(
            db_session,
            agent_id=UUID(sample_agent["id"]),
            user_id=test_user_id,
        )

        # Create message
        message = await msg_repo.create(
            db_session,
            conversation_id=conversation.id,
            role="user",
            content="Hello, world!",
        )

        assert message.id is not None
        assert message.role == "user"
        assert message.content == "Hello, world!"

    @pytest.mark.asyncio
    async def test_list_messages_by_conversation(
        self, db_session: AsyncSession, sample_agent: dict, test_user_id: UUID
    ):
        """Test listing messages for a conversation."""
        conv_repo = ConversationRepository()
        msg_repo = MessageRepository()

        # Create conversation
        conversation = await conv_repo.create(
            db_session,
            agent_id=UUID(sample_agent["id"]),
            user_id=test_user_id,
        )

        # Create messages
        await msg_repo.create(
            db_session,
            conversation_id=conversation.id,
            role="user",
            content="Hello",
        )
        await msg_repo.create(
            db_session,
            conversation_id=conversation.id,
            role="assistant",
            content="Hi there!",
        )
        await db_session.flush()

        # List messages
        messages = await msg_repo.list_by_conversation(db_session, conversation.id)
        assert len(messages) >= 2
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"

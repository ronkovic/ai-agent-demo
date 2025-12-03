"""Repository pattern for data access."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    Agent,
    AgentCard,
    Conversation,
    Message,
    PersonalAgent,
    ScheduleTrigger,
    UserApiKey,
    UserLLMConfig,
    WebhookTrigger,
    Workflow,
    WorkflowExecution,
)

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


# =============================================================================
# Personal Agent Repository
# =============================================================================


class PersonalAgentRepository:
    """PersonalAgent data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        name: str,
        system_prompt: str,
        description: str | None = None,
        is_public: bool = False,
    ) -> PersonalAgent:
        """Create a new personal agent."""
        agent = PersonalAgent(
            user_id=user_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            is_public=is_public,
        )
        db.add(agent)
        await db.flush()
        await db.refresh(agent)
        return agent

    async def get(self, db: AsyncSession, agent_id: UUID) -> PersonalAgent | None:
        """Get personal agent by ID."""
        result = await db.execute(select(PersonalAgent).where(PersonalAgent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_by_user(
        self, db: AsyncSession, agent_id: UUID, user_id: UUID
    ) -> PersonalAgent | None:
        """Get personal agent by ID and user ID."""
        result = await db.execute(
            select(PersonalAgent).where(
                PersonalAgent.id == agent_id, PersonalAgent.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, db: AsyncSession, user_id: UUID) -> list[PersonalAgent]:
        """List all personal agents for a user."""
        result = await db.execute(
            select(PersonalAgent)
            .where(PersonalAgent.user_id == user_id)
            .order_by(PersonalAgent.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        agent: PersonalAgent,
        **kwargs: str | bool | None,
    ) -> PersonalAgent:
        """Update personal agent fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(agent, key):
                setattr(agent, key, value)
        await db.flush()
        await db.refresh(agent)
        return agent

    async def delete(self, db: AsyncSession, agent: PersonalAgent) -> None:
        """Delete a personal agent."""
        await db.delete(agent)
        await db.flush()


# =============================================================================
# User LLM Config Repository
# =============================================================================


class UserLLMConfigRepository:
    """UserLLMConfig data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        provider: str,
        vault_secret_id: str,
        is_default: bool = False,
    ) -> UserLLMConfig:
        """Create a new LLM config."""
        config = UserLLMConfig(
            user_id=user_id,
            provider=provider,
            vault_secret_id=vault_secret_id,
            is_default=is_default,
        )
        db.add(config)
        await db.flush()
        await db.refresh(config)
        return config

    async def get(self, db: AsyncSession, config_id: UUID) -> UserLLMConfig | None:
        """Get LLM config by ID."""
        result = await db.execute(select(UserLLMConfig).where(UserLLMConfig.id == config_id))
        return result.scalar_one_or_none()

    async def get_by_user(
        self, db: AsyncSession, config_id: UUID, user_id: UUID
    ) -> UserLLMConfig | None:
        """Get LLM config by ID and user ID."""
        result = await db.execute(
            select(UserLLMConfig).where(
                UserLLMConfig.id == config_id, UserLLMConfig.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_provider(
        self, db: AsyncSession, user_id: UUID, provider: str
    ) -> UserLLMConfig | None:
        """Get LLM config by user ID and provider."""
        result = await db.execute(
            select(UserLLMConfig).where(
                UserLLMConfig.user_id == user_id, UserLLMConfig.provider == provider
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, db: AsyncSession, user_id: UUID) -> list[UserLLMConfig]:
        """List all LLM configs for a user."""
        result = await db.execute(
            select(UserLLMConfig)
            .where(UserLLMConfig.user_id == user_id)
            .order_by(UserLLMConfig.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, db: AsyncSession, config: UserLLMConfig) -> None:
        """Delete a LLM config."""
        await db.delete(config)
        await db.flush()


# =============================================================================
# User API Key Repository
# =============================================================================


class UserApiKeyRepository:
    """UserApiKey data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        name: str,
        key_hash: str,
        key_prefix: str,
        scopes: list[str] | None = None,
        rate_limit: int = 1000,
        expires_at: datetime | None = None,
    ) -> UserApiKey:
        """Create a new API key."""
        api_key = UserApiKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=scopes or [],
            rate_limit=rate_limit,
            expires_at=expires_at,
        )
        db.add(api_key)
        await db.flush()
        await db.refresh(api_key)
        return api_key

    async def get(self, db: AsyncSession, key_id: UUID) -> UserApiKey | None:
        """Get API key by ID."""
        result = await db.execute(select(UserApiKey).where(UserApiKey.id == key_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, db: AsyncSession, key_id: UUID, user_id: UUID) -> UserApiKey | None:
        """Get API key by ID and user ID."""
        result = await db.execute(
            select(UserApiKey).where(UserApiKey.id == key_id, UserApiKey.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_hash(self, db: AsyncSession, key_hash: str) -> UserApiKey | None:
        """Get API key by hash (for authentication)."""
        result = await db.execute(select(UserApiKey).where(UserApiKey.key_hash == key_hash))
        return result.scalar_one_or_none()

    async def list_by_user(self, db: AsyncSession, user_id: UUID) -> list[UserApiKey]:
        """List all API keys for a user."""
        result = await db.execute(
            select(UserApiKey)
            .where(UserApiKey.user_id == user_id)
            .order_by(UserApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_last_used(self, db: AsyncSession, api_key: UserApiKey) -> None:
        """Update last used timestamp."""
        api_key.last_used_at = datetime.now(UTC)
        await db.flush()

    async def delete(self, db: AsyncSession, api_key: UserApiKey) -> None:
        """Delete an API key."""
        await db.delete(api_key)
        await db.flush()


# =============================================================================
# Workflow Repository
# =============================================================================


class WorkflowRepository:
    """Workflow data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        name: str,
        description: str | None = None,
        nodes: list[dict] | None = None,
        edges: list[dict] | None = None,
        trigger_config: dict | None = None,
        is_active: bool = True,
    ) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(
            user_id=user_id,
            name=name,
            description=description,
            nodes=nodes or [],
            edges=edges or [],
            trigger_config=trigger_config or {},
            is_active=is_active,
        )
        db.add(workflow)
        await db.flush()
        await db.refresh(workflow)
        return workflow

    async def get(self, db: AsyncSession, workflow_id: UUID) -> Workflow | None:
        """Get workflow by ID."""
        result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        return result.scalar_one_or_none()

    async def get_by_user(
        self, db: AsyncSession, workflow_id: UUID, user_id: UUID
    ) -> Workflow | None:
        """Get workflow by ID and user ID."""
        result = await db.execute(
            select(Workflow).where(Workflow.id == workflow_id, Workflow.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, db: AsyncSession, user_id: UUID) -> list[Workflow]:
        """List all workflows for a user."""
        result = await db.execute(
            select(Workflow).where(Workflow.user_id == user_id).order_by(Workflow.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        workflow: Workflow,
        **kwargs: str | bool | list | dict | None,
    ) -> Workflow:
        """Update workflow fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(workflow, key):
                setattr(workflow, key, value)
        await db.flush()
        await db.refresh(workflow)
        return workflow

    async def delete(self, db: AsyncSession, workflow: Workflow) -> None:
        """Delete a workflow."""
        await db.delete(workflow)
        await db.flush()


# =============================================================================
# Workflow Execution Repository
# =============================================================================


class WorkflowExecutionRepository:
    """WorkflowExecution data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        workflow_id: UUID,
        status: str = "pending",
        trigger_data: dict | None = None,
    ) -> WorkflowExecution:
        """Create a new workflow execution."""
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=status,
            trigger_data=trigger_data,
            node_results={},
        )
        db.add(execution)
        await db.flush()
        await db.refresh(execution)
        return execution

    async def get(self, db: AsyncSession, execution_id: UUID) -> WorkflowExecution | None:
        """Get execution by ID."""
        result = await db.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def list_by_workflow(
        self, db: AsyncSession, workflow_id: UUID, limit: int = 50
    ) -> list[WorkflowExecution]:
        """List all executions for a workflow."""
        result = await db.execute(
            select(WorkflowExecution)
            .where(WorkflowExecution.workflow_id == workflow_id)
            .order_by(WorkflowExecution.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        db: AsyncSession,
        execution: WorkflowExecution,
        status: str,
        node_results: dict | None = None,
        error: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> WorkflowExecution:
        """Update execution status."""
        execution.status = status
        if node_results is not None:
            execution.node_results = node_results
        if error is not None:
            execution.error = error
        if started_at is not None:
            execution.started_at = started_at
        if completed_at is not None:
            execution.completed_at = completed_at
        await db.flush()
        await db.refresh(execution)
        return execution

    async def update_node_result(
        self,
        db: AsyncSession,
        execution: WorkflowExecution,
        node_id: str,
        result: dict,
    ) -> WorkflowExecution:
        """Update a single node result."""
        execution.node_results[node_id] = result
        await db.flush()
        await db.refresh(execution)
        return execution


# =============================================================================
# Schedule Trigger Repository
# =============================================================================


class ScheduleTriggerRepository:
    """ScheduleTrigger data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        workflow_id: UUID,
        cron_expression: str,
        timezone: str = "UTC",
        is_active: bool = True,
    ) -> ScheduleTrigger:
        """Create a new schedule trigger."""
        trigger = ScheduleTrigger(
            workflow_id=workflow_id,
            cron_expression=cron_expression,
            timezone=timezone,
            is_active=is_active,
        )
        db.add(trigger)
        await db.flush()
        await db.refresh(trigger)
        return trigger

    async def get(self, db: AsyncSession, trigger_id: UUID) -> ScheduleTrigger | None:
        """Get schedule trigger by ID."""
        result = await db.execute(
            select(ScheduleTrigger).where(ScheduleTrigger.id == trigger_id)
        )
        return result.scalar_one_or_none()

    async def list_by_workflow(
        self, db: AsyncSession, workflow_id: UUID
    ) -> list[ScheduleTrigger]:
        """List all schedule triggers for a workflow."""
        result = await db.execute(
            select(ScheduleTrigger)
            .where(ScheduleTrigger.workflow_id == workflow_id)
            .order_by(ScheduleTrigger.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_active(self, db: AsyncSession) -> list[ScheduleTrigger]:
        """List all active schedule triggers."""
        result = await db.execute(
            select(ScheduleTrigger)
            .where(ScheduleTrigger.is_active == True)  # noqa: E712
            .options(selectinload(ScheduleTrigger.workflow))
        )
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        trigger: ScheduleTrigger,
        **kwargs: str | bool | datetime | None,
    ) -> ScheduleTrigger:
        """Update schedule trigger fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(trigger, key):
                setattr(trigger, key, value)
        await db.flush()
        await db.refresh(trigger)
        return trigger

    async def delete(self, db: AsyncSession, trigger: ScheduleTrigger) -> None:
        """Delete a schedule trigger."""
        await db.delete(trigger)
        await db.flush()


# =============================================================================
# Webhook Trigger Repository
# =============================================================================


class WebhookTriggerRepository:
    """WebhookTrigger data access repository."""

    async def create(
        self,
        db: AsyncSession,
        *,
        workflow_id: UUID,
        webhook_path: str,
        secret: str | None = None,
        is_active: bool = True,
    ) -> WebhookTrigger:
        """Create a new webhook trigger."""
        trigger = WebhookTrigger(
            workflow_id=workflow_id,
            webhook_path=webhook_path,
            secret=secret,
            is_active=is_active,
        )
        db.add(trigger)
        await db.flush()
        await db.refresh(trigger)
        return trigger

    async def get(self, db: AsyncSession, trigger_id: UUID) -> WebhookTrigger | None:
        """Get webhook trigger by ID."""
        result = await db.execute(
            select(WebhookTrigger).where(WebhookTrigger.id == trigger_id)
        )
        return result.scalar_one_or_none()

    async def get_by_path(
        self, db: AsyncSession, webhook_path: str
    ) -> WebhookTrigger | None:
        """Get webhook trigger by path."""
        result = await db.execute(
            select(WebhookTrigger)
            .where(WebhookTrigger.webhook_path == webhook_path)
            .where(WebhookTrigger.is_active == True)  # noqa: E712
            .options(selectinload(WebhookTrigger.workflow))
        )
        return result.scalar_one_or_none()

    async def list_by_workflow(
        self, db: AsyncSession, workflow_id: UUID
    ) -> list[WebhookTrigger]:
        """List all webhook triggers for a workflow."""
        result = await db.execute(
            select(WebhookTrigger)
            .where(WebhookTrigger.workflow_id == workflow_id)
            .order_by(WebhookTrigger.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        trigger: WebhookTrigger,
        **kwargs: str | bool | datetime | None,
    ) -> WebhookTrigger:
        """Update webhook trigger fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(trigger, key):
                setattr(trigger, key, value)
        await db.flush()
        await db.refresh(trigger)
        return trigger

    async def delete(self, db: AsyncSession, trigger: WebhookTrigger) -> None:
        """Delete a webhook trigger."""
        await db.delete(trigger)
        await db.flush()

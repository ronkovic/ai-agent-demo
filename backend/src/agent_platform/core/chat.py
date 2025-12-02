"""Chat service for handling conversations with agents."""

import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..db import Agent, ConversationRepository, MessageRepository
from ..llm import ChatMessage as LLMChatMessage
from ..llm import LLMProvider, ToolCall, to_litellm_tools
from ..tools import ToolRegistry, ToolResult
from .executor import ToolExecutor

logger = logging.getLogger(__name__)


@dataclass
class ChatEvent:
    """Chat event for streaming responses."""

    type: str  # 'content', 'tool_call', 'tool_result', 'done', 'error'
    data: Any


class ChatService:
    """Service for handling chat conversations with agents."""

    MAX_TOOL_ITERATIONS = 5  # Prevent infinite tool loops

    def __init__(
        self,
        llm: LLMProvider,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        executor: ToolExecutor | None = None,
    ):
        """Initialize chat service.

        Args:
            llm: LLM provider for generating responses.
            conversation_repo: Repository for conversation data.
            message_repo: Repository for message data.
            executor: Optional tool executor (created if not provided).
        """
        self.llm = llm
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.executor = executor or ToolExecutor()

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

    def _get_tools_for_agent(self, agent: Agent) -> list[dict[str, Any]] | None:
        """Get LLM-formatted tools for an agent.

        Args:
            agent: Agent with tools configuration.

        Returns:
            List of tools in LiteLLM format, or None if no tools.
        """
        if not agent.tools:
            return None

        tool_names = agent.tools if isinstance(agent.tools, list) else []
        if not tool_names:
            return None

        definitions = ToolRegistry.get_definitions(tool_names)
        if not definitions:
            return None

        return to_litellm_tools(definitions)

    async def _execute_tool_calls(
        self,
        tool_calls: list[ToolCall],
    ) -> list[tuple[ToolCall, ToolResult]]:
        """Execute tool calls and return results.

        Args:
            tool_calls: List of tool calls from LLM.

        Returns:
            List of (tool_call, result) tuples.
        """
        results = []
        for tc in tool_calls:
            result = await self.executor.execute(tc.name, tc.arguments)
            results.append((tc, result))
        return results

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

        # Get tools for agent
        tools = self._get_tools_for_agent(agent)

        # Reset executor for new turn
        self.executor.reset_call_count()

        # Tool execution loop
        iteration = 0
        while iteration < self.MAX_TOOL_ITERATIONS:
            iteration += 1

            # Get LLM response
            response = await self.llm.chat_with_tools(
                messages=messages,
                model=agent.llm_model,
                tools=tools,
            )

            # If no tool calls, we're done
            if not response.has_tool_calls:
                break

            # Execute tool calls
            tool_results = await self._execute_tool_calls(response.tool_calls)

            # Add tool calls and results to messages
            for tc, result in tool_results:
                # Add assistant's tool call (as content for now)
                tool_call_info = {
                    "tool_call_id": tc.id,
                    "name": tc.name,
                    "arguments": tc.arguments,
                }
                messages.append(
                    LLMChatMessage(
                        role="assistant",
                        content=f"Calling tool: {tc.name}",
                    )
                )

                # Add tool result
                messages.append(
                    LLMChatMessage(
                        role="tool",
                        content=json.dumps(result.to_dict()),
                        tool_call_id=tc.id,
                    )
                )

                # Save tool call and result to database
                await self.message_repo.create(
                    db,
                    conversation_id=conv_id,
                    role="assistant",
                    content=f"Calling tool: {tc.name}",
                    tool_calls=tool_call_info,
                )
                await self.message_repo.create(
                    db,
                    conversation_id=conv_id,
                    role="tool",
                    content=json.dumps(result.to_dict()),
                )

        # Save final assistant message
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
        """Handle a streaming chat message (simple, without tools).

        For backwards compatibility, this method streams without tool support.
        Use chat_stream_with_tools for full tool support.

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

        # Build messages for LLM
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

    async def chat_stream_with_tools(
        self,
        db: AsyncSession,
        agent: Agent,
        user_id: UUID,
        user_message: str,
        conversation_id: UUID | None = None,
    ) -> tuple[UUID, AsyncIterator[ChatEvent]]:
        """Handle a streaming chat message with tool support.

        This method yields ChatEvent objects that can include:
        - content: Text content chunks
        - tool_call: Tool is being called
        - tool_result: Tool execution result
        - done: Stream completed
        - error: Error occurred

        Args:
            db: Database session.
            agent: Agent to chat with.
            user_id: User ID.
            user_message: User's message.
            conversation_id: Optional existing conversation ID.

        Returns:
            Tuple of (conversation_id, async iterator of ChatEvents).
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

        # Get tools for agent
        tools = self._get_tools_for_agent(agent)

        # Reset executor for new turn
        self.executor.reset_call_count()

        async def stream_with_tools() -> AsyncIterator[ChatEvent]:
            """Stream response with tool handling."""
            nonlocal messages

            iteration = 0
            while iteration < self.MAX_TOOL_ITERATIONS:
                iteration += 1

                # Get LLM response (non-streaming for tool handling)
                response = await self.llm.chat_with_tools(
                    messages=messages,
                    model=agent.llm_model,
                    tools=tools,
                )

                # If tool calls, execute them
                if response.has_tool_calls:
                    for tc in response.tool_calls:
                        # Emit tool call event
                        yield ChatEvent(
                            type="tool_call",
                            data={
                                "id": tc.id,
                                "name": tc.name,
                                "arguments": tc.arguments,
                            },
                        )

                        # Execute tool
                        result = await self.executor.execute(tc.name, tc.arguments)

                        # Emit tool result event
                        yield ChatEvent(
                            type="tool_result",
                            data={
                                "tool_call_id": tc.id,
                                "success": result.success,
                                "output": result.output,
                                "error": result.error,
                            },
                        )

                        # Add to messages for next iteration
                        messages.append(
                            LLMChatMessage(
                                role="assistant",
                                content=f"Calling tool: {tc.name}",
                            )
                        )
                        messages.append(
                            LLMChatMessage(
                                role="tool",
                                content=json.dumps(result.to_dict()),
                                tool_call_id=tc.id,
                            )
                        )

                        # Save to database
                        tool_call_info = {
                            "tool_call_id": tc.id,
                            "name": tc.name,
                            "arguments": tc.arguments,
                        }
                        await self.message_repo.create(
                            db,
                            conversation_id=conv_id,
                            role="assistant",
                            content=f"Calling tool: {tc.name}",
                            tool_calls=tool_call_info,
                        )
                        await self.message_repo.create(
                            db,
                            conversation_id=conv_id,
                            role="tool",
                            content=json.dumps(result.to_dict()),
                        )

                    # Continue to get final response
                    continue

                # No tool calls - emit content and finish
                if response.content:
                    yield ChatEvent(type="content", data=response.content)

                    # Save final response
                    await self.message_repo.create(
                        db,
                        conversation_id=conv_id,
                        role="assistant",
                        content=response.content,
                    )

                yield ChatEvent(type="done", data={})
                break

        return conv_id, stream_with_tools()

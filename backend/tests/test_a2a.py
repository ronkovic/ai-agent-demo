"""A2A (Agent-to-Agent) プロトコル テスト."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.a2a import (
    A2A_SYSTEM_USER_ID,
    A2AClient,
    A2AClientError,
    A2ATaskContext,
    A2ATaskStatus,
    TaskStore,
    clear_all_stores,
    extract_text_from_message,
    generate_agent_card,
    get_task_store,
)
from agent_platform.db import AgentRepository
from agent_platform.tools.a2a import InvokeAgentTool


class TestA2ATypes:
    """A2A型定義テスト."""

    def test_task_status_values(self):
        """タスクステータスの値を確認."""
        assert A2ATaskStatus.PENDING.value == "pending"
        assert A2ATaskStatus.RUNNING.value == "running"
        assert A2ATaskStatus.COMPLETED.value == "completed"
        assert A2ATaskStatus.FAILED.value == "failed"
        assert A2ATaskStatus.CANCELLED.value == "cancelled"

    def test_task_context_creation(self):
        """タスクコンテキスト作成を確認."""
        agent_id = uuid4()
        context = A2ATaskContext(
            task_id="test-task-123",
            agent_id=agent_id,
            status=A2ATaskStatus.PENDING,
        )

        assert context.task_id == "test-task-123"
        assert context.agent_id == agent_id
        assert context.status == A2ATaskStatus.PENDING
        assert context.conversation_id is None
        assert context.result is None
        assert context.error is None

    def test_task_context_to_dict(self):
        """タスクコンテキストの辞書変換を確認."""
        agent_id = uuid4()
        conv_id = uuid4()
        context = A2ATaskContext(
            task_id="test-task-456",
            agent_id=agent_id,
            conversation_id=conv_id,
            status=A2ATaskStatus.COMPLETED,
            result={"response": "Hello"},
        )

        d = context.to_dict()
        assert d["task_id"] == "test-task-456"
        assert d["agent_id"] == str(agent_id)
        assert d["conversation_id"] == str(conv_id)
        assert d["status"] == "completed"
        assert d["result"] == {"response": "Hello"}

    def test_system_user_id(self):
        """システムユーザーIDを確認."""
        assert A2A_SYSTEM_USER_ID == UUID("00000000-0000-0000-0000-000000000002")


class TestAgentCard:
    """Agent Card生成テスト."""

    def test_generate_agent_card_basic(self):
        """基本的なAgent Card生成を確認."""
        mock_agent = MagicMock()
        mock_agent.id = uuid4()
        mock_agent.name = "Test Agent"
        mock_agent.description = "A test agent for testing"
        mock_agent.tools = []

        card = generate_agent_card(mock_agent)

        assert card["name"] == "Test Agent"
        assert card["description"] == "A test agent for testing"
        assert card["version"] == "1.0.0"
        assert card["protocolVersion"] == "0.3.0"
        assert card["capabilities"]["streaming"] is True
        assert card["capabilities"]["pushNotifications"] is False

    def test_generate_agent_card_with_tools(self):
        """ツール付きAgent Card生成を確認."""
        mock_agent = MagicMock()
        mock_agent.id = uuid4()
        mock_agent.name = "Code Agent"
        mock_agent.description = "Code execution agent"
        mock_agent.tools = ["code_execution", "web_search"]

        card = generate_agent_card(mock_agent)

        skill_ids = [s["id"] for s in card["skills"]]
        assert "code_execution" in skill_ids
        assert "web_search" in skill_ids
        assert "conversation" in skill_ids  # デフォルトスキル

    def test_generate_agent_card_url(self):
        """Agent Card URLを確認."""
        mock_agent = MagicMock()
        mock_agent.id = uuid4()
        mock_agent.name = "Test Agent"
        mock_agent.description = None
        mock_agent.tools = []

        card = generate_agent_card(mock_agent)

        assert str(mock_agent.id) in card["url"]


class TestTaskStore:
    """タスクストア テスト."""

    @pytest_asyncio.fixture
    async def task_store(self):
        """テスト用タスクストアを作成."""
        store = TaskStore()
        yield store
        await store.clear()

    @pytest.mark.asyncio
    async def test_save_and_get_task(self, task_store: TaskStore):
        """タスクの保存と取得を確認."""
        task_data = {
            "id": "task-001",
            "status": "running",
            "agent_id": str(uuid4()),
        }

        await task_store.save_task("task-001", task_data)
        retrieved = await task_store.get_task("task-001")

        assert retrieved is not None
        assert retrieved["id"] == "task-001"
        assert retrieved["status"] == "running"

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, task_store: TaskStore):
        """存在しないタスクの取得を確認."""
        result = await task_store.get_task("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_save_and_get_context(self, task_store: TaskStore):
        """コンテキストの保存と取得を確認."""
        agent_id = uuid4()
        context = A2ATaskContext(
            task_id="task-002",
            agent_id=agent_id,
            status=A2ATaskStatus.PENDING,
        )

        await task_store.save_context(context)
        retrieved = await task_store.get_context("task-002")

        assert retrieved is not None
        assert retrieved.task_id == "task-002"
        assert retrieved.agent_id == agent_id

    @pytest.mark.asyncio
    async def test_update_context_status(self, task_store: TaskStore):
        """コンテキストステータス更新を確認."""
        agent_id = uuid4()
        context = A2ATaskContext(
            task_id="task-003",
            agent_id=agent_id,
            status=A2ATaskStatus.PENDING,
        )

        await task_store.save_context(context)
        updated = await task_store.update_context_status(
            "task-003",
            A2ATaskStatus.COMPLETED,
            result={"message": "Done"},
        )

        assert updated is not None
        assert updated.status == A2ATaskStatus.COMPLETED
        assert updated.result == {"message": "Done"}

    @pytest.mark.asyncio
    async def test_set_conversation_id(self, task_store: TaskStore):
        """conversation_id設定を確認."""
        agent_id = uuid4()
        conv_id = uuid4()
        context = A2ATaskContext(
            task_id="task-004",
            agent_id=agent_id,
        )

        await task_store.save_context(context)
        updated = await task_store.set_conversation_id("task-004", conv_id)

        assert updated is not None
        assert updated.conversation_id == conv_id

    @pytest.mark.asyncio
    async def test_delete_task(self, task_store: TaskStore):
        """タスク削除を確認."""
        agent_id = uuid4()
        context = A2ATaskContext(task_id="task-005", agent_id=agent_id)

        await task_store.save_task("task-005", {"id": "task-005"})
        await task_store.save_context(context)
        await task_store.delete_task("task-005")

        assert await task_store.get_task("task-005") is None
        assert await task_store.get_context("task-005") is None

    @pytest.mark.asyncio
    async def test_list_tasks_by_agent(self, task_store: TaskStore):
        """エージェントごとのタスク一覧を確認."""
        agent_id_1 = uuid4()
        agent_id_2 = uuid4()

        await task_store.save_context(
            A2ATaskContext(task_id="task-a1", agent_id=agent_id_1)
        )
        await task_store.save_context(
            A2ATaskContext(task_id="task-a2", agent_id=agent_id_1)
        )
        await task_store.save_context(
            A2ATaskContext(task_id="task-b1", agent_id=agent_id_2)
        )

        agent_1_tasks = await task_store.list_tasks_by_agent(agent_id_1)
        agent_2_tasks = await task_store.list_tasks_by_agent(agent_id_2)

        assert len(agent_1_tasks) == 2
        assert len(agent_2_tasks) == 1


class TestGetTaskStore:
    """get_task_store関数テスト."""

    @pytest.mark.asyncio
    async def test_get_task_store_creates_new(self):
        """新しいストアを作成することを確認."""
        await clear_all_stores()
        agent_id = uuid4()

        store = await get_task_store(agent_id)

        assert isinstance(store, TaskStore)

    @pytest.mark.asyncio
    async def test_get_task_store_returns_same(self):
        """同じエージェントには同じストアを返すことを確認."""
        await clear_all_stores()
        agent_id = uuid4()

        store1 = await get_task_store(agent_id)
        store2 = await get_task_store(agent_id)

        assert store1 is store2


class TestExtractTextFromMessage:
    """extract_text_from_message関数テスト."""

    def test_extract_from_text_parts(self):
        """TextPart形式からテキスト抽出を確認."""
        message = {
            "role": "user",
            "parts": [
                {"type": "text", "text": "Hello"},
                {"type": "text", "text": "World"},
            ],
        }

        result = extract_text_from_message(message)
        assert result == "Hello World"

    def test_extract_from_dict_with_text(self):
        """text属性を持つdict形式からの抽出を確認."""
        message = {
            "role": "user",
            "parts": [{"text": "Simple message"}],
        }

        result = extract_text_from_message(message)
        assert result == "Simple message"

    def test_extract_from_string_parts(self):
        """文字列parts形式からの抽出を確認."""
        message = {
            "role": "user",
            "parts": ["Direct", "strings"],
        }

        result = extract_text_from_message(message)
        assert result == "Direct strings"

    def test_extract_empty_message(self):
        """空メッセージの処理を確認."""
        message = {"role": "user", "parts": []}

        result = extract_text_from_message(message)
        assert result == ""


class TestInvokeAgentTool:
    """InvokeAgentToolテスト."""

    def test_tool_definition(self):
        """ツール定義を確認."""
        tool = InvokeAgentTool()
        definition = tool.definition

        assert definition.name == "invoke_agent"
        assert len(definition.parameters) == 3

        param_names = [p.name for p in definition.parameters]
        assert "agent_url" in param_names
        assert "message" in param_names
        assert "wait_for_completion" in param_names

    @pytest.mark.asyncio
    async def test_execute_missing_agent_url(self):
        """agent_url未指定時のエラーを確認."""
        tool = InvokeAgentTool()

        result = await tool.execute(message="Hello")

        assert result.success is False
        assert "agent_url is required" in result.error

    @pytest.mark.asyncio
    async def test_execute_missing_message(self):
        """message未指定時のエラーを確認."""
        tool = InvokeAgentTool()

        result = await tool.execute(agent_url="http://test.local/agent")

        assert result.success is False
        assert "message is required" in result.error

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """正常実行を確認."""
        mock_client = AsyncMock(spec=A2AClient)
        mock_client.get_agent_card.return_value = {"name": "Test Agent"}
        mock_client.send_task.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {
                "message": {
                    "role": "agent",
                    "parts": [{"type": "text", "text": "Response"}],
                }
            },
        }

        tool = InvokeAgentTool(client=mock_client)

        result = await tool.execute(
            agent_url="http://test.local/agent",
            message="Hello",
        )

        assert result.success is True
        assert result.output["status"] == "completed"
        assert result.output["response"] == "Response"

    @pytest.mark.asyncio
    async def test_execute_wait_false(self):
        """wait_for_completion=Falseの動作を確認."""
        mock_client = AsyncMock(spec=A2AClient)
        mock_client.get_agent_card.return_value = {"name": "Test Agent"}
        mock_client.send_task.return_value = {
            "id": "task-456",
            "status": "running",
        }

        tool = InvokeAgentTool(client=mock_client)

        result = await tool.execute(
            agent_url="http://test.local/agent",
            message="Hello",
            wait_for_completion=False,
        )

        assert result.success is True
        assert result.output["task_id"] == "task-456"
        assert "Task submitted" in result.output["message"]

    @pytest.mark.asyncio
    async def test_execute_agent_not_found(self):
        """エージェント未発見時のエラーを確認."""
        mock_client = AsyncMock(spec=A2AClient)
        mock_client.get_agent_card.side_effect = A2AClientError(
            "Not found", status_code=404
        )

        tool = InvokeAgentTool(client=mock_client)

        result = await tool.execute(
            agent_url="http://test.local/agent",
            message="Hello",
        )

        assert result.success is False
        assert "Agent not found" in result.error


class TestA2AEndpoints:
    """A2A APIエンドポイントテスト."""

    @pytest_asyncio.fixture
    async def a2a_enabled_agent(
        self, db_session: AsyncSession, test_user_id: UUID
    ) -> dict:
        """A2A有効なエージェントを作成."""
        repo = AgentRepository()
        agent = await repo.create(
            db_session,
            user_id=test_user_id,
            name="A2A Test Agent",
            description="Agent for A2A testing",
            system_prompt="You are an A2A test agent.",
            llm_provider="claude",
            llm_model="claude-3-5-sonnet-20241022",
            tools=["code_execution"],
            a2a_enabled=True,
        )

        return {
            "id": str(agent.id),
            "name": agent.name,
            "description": agent.description,
        }

    @pytest.mark.asyncio
    async def test_get_agent_card(self, client: AsyncClient, a2a_enabled_agent: dict):
        """Agent Card取得エンドポイントを確認."""
        agent_id = a2a_enabled_agent["id"]

        response = await client.get(
            f"/a2a/agents/{agent_id}/.well-known/agent.json"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "A2A Test Agent"
        assert "capabilities" in data
        assert "skills" in data

    @pytest.mark.asyncio
    async def test_get_agent_card_not_found(self, client: AsyncClient):
        """存在しないエージェントのAgent Card取得を確認."""
        fake_id = str(uuid4())

        response = await client.get(
            f"/a2a/agents/{fake_id}/.well-known/agent.json"
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_agent_card_a2a_disabled(
        self, client: AsyncClient, sample_agent: dict
    ):
        """A2A無効エージェントへのアクセスを確認."""
        agent_id = sample_agent["id"]

        response = await client.get(
            f"/a2a/agents/{agent_id}/.well-known/agent.json"
        )

        assert response.status_code == 403
        assert "A2A is not enabled" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_task(self, client: AsyncClient, a2a_enabled_agent: dict):
        """タスク作成エンドポイントを確認."""
        agent_id = a2a_enabled_agent["id"]

        # ChatServiceをモック
        with patch(
            "agent_platform.a2a.server.ChatService"
        ) as mock_chat_service_class:
            mock_chat_service = AsyncMock()
            mock_chat_service.chat.return_value = (uuid4(), "Hello response")
            mock_chat_service_class.return_value = mock_chat_service

            response = await client.post(
                f"/a2a/agents/{agent_id}/tasks",
                json={
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": "Hello agent"}],
                    }
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] in ["completed", "running", "failed"]

    @pytest.mark.asyncio
    async def test_create_task_empty_message(
        self, client: AsyncClient, a2a_enabled_agent: dict
    ):
        """空メッセージでのタスク作成を確認."""
        agent_id = a2a_enabled_agent["id"]

        response = await client.post(
            f"/a2a/agents/{agent_id}/tasks",
            json={
                "message": {
                    "role": "user",
                    "parts": [],
                }
            },
        )

        assert response.status_code == 400
        assert "text content" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_task_not_found(
        self, client: AsyncClient, a2a_enabled_agent: dict
    ):
        """存在しないタスクの取得を確認."""
        agent_id = a2a_enabled_agent["id"]

        response = await client.get(
            f"/a2a/agents/{agent_id}/tasks/nonexistent-task"
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_task_not_found(
        self, client: AsyncClient, a2a_enabled_agent: dict
    ):
        """存在しないタスクのキャンセルを確認."""
        agent_id = a2a_enabled_agent["id"]

        response = await client.post(
            f"/a2a/agents/{agent_id}/tasks/nonexistent-task/cancel"
        )

        assert response.status_code == 404

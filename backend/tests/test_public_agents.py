"""公開エージェントAPIテスト."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from agent_platform.db.models import Agent


class TestPublicAgentAPI:
    """公開エージェントAPIテスト."""

    @pytest.mark.asyncio
    async def test_list_public_agents(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """公開エージェント一覧取得."""
        response = await client.get("/api/agents/public")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_search_public_agents(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """公開エージェント検索."""
        response = await client.get("/api/agents/public/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_search_requires_query(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """検索クエリは必須."""
        response = await client.get("/api/agents/public/search")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_public_agent(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """公開エージェント作成."""
        response = await client.post(
            "/api/agents",
            json={
                "name": "Public Test Agent",
                "description": "A public test agent",
                "system_prompt": "You are a helpful assistant.",
                "llm_provider": "claude",
                "llm_model": "claude-3-5-sonnet-20241022",
                "is_public": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["is_public"] is True
        assert data["name"] == "Public Test Agent"

    @pytest.mark.asyncio
    async def test_create_private_agent(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """非公開エージェント作成 (デフォルト)."""
        response = await client.post(
            "/api/agents",
            json={
                "name": "Private Test Agent",
                "system_prompt": "You are a helpful assistant.",
                "llm_provider": "claude",
                "llm_model": "claude-3-5-sonnet-20241022",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["is_public"] is False

    @pytest.mark.asyncio
    async def test_update_agent_to_public(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """エージェントを公開に更新."""
        # Create a private agent
        create_response = await client.post(
            "/api/agents",
            json={
                "name": "Update Test Agent",
                "system_prompt": "You are a helpful assistant.",
                "llm_provider": "claude",
                "llm_model": "claude-3-5-sonnet-20241022",
                "is_public": False,
            },
        )
        assert create_response.status_code == 201
        agent_id = create_response.json()["id"]

        # Update to public
        update_response = await client.patch(
            f"/api/agents/{agent_id}",
            json={"is_public": True},
        )
        assert update_response.status_code == 200
        assert update_response.json()["is_public"] is True

    @pytest.mark.asyncio
    async def test_public_agent_in_list(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """公開エージェントは公開一覧に含まれる."""
        # Create a public agent
        create_response = await client.post(
            "/api/agents",
            json={
                "name": f"Public Agent {uuid4().hex[:8]}",
                "system_prompt": "You are a helpful assistant.",
                "llm_provider": "claude",
                "llm_model": "claude-3-5-sonnet-20241022",
                "is_public": True,
            },
        )
        assert create_response.status_code == 201
        agent_id = create_response.json()["id"]

        # Check public list
        list_response = await client.get("/api/agents/public")
        assert list_response.status_code == 200
        agents = list_response.json()
        assert any(a["id"] == agent_id for a in agents)

    @pytest.mark.asyncio
    async def test_private_agent_not_in_public_list(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """非公開エージェントは公開一覧に含まれない."""
        # Create a private agent
        create_response = await client.post(
            "/api/agents",
            json={
                "name": f"Private Agent {uuid4().hex[:8]}",
                "system_prompt": "You are a helpful assistant.",
                "llm_provider": "claude",
                "llm_model": "claude-3-5-sonnet-20241022",
                "is_public": False,
            },
        )
        assert create_response.status_code == 201
        agent_id = create_response.json()["id"]

        # Check public list
        list_response = await client.get("/api/agents/public")
        assert list_response.status_code == 200
        agents = list_response.json()
        assert not any(a["id"] == agent_id for a in agents)

    @pytest.mark.asyncio
    async def test_public_response_no_system_prompt(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """公開エージェントレスポンスにはsystem_promptが含まれない."""
        # Create a public agent
        create_response = await client.post(
            "/api/agents",
            json={
                "name": f"Public Agent {uuid4().hex[:8]}",
                "system_prompt": "Secret prompt that should not be exposed.",
                "llm_provider": "claude",
                "llm_model": "claude-3-5-sonnet-20241022",
                "is_public": True,
            },
        )
        assert create_response.status_code == 201
        agent_id = create_response.json()["id"]

        # Check public list
        list_response = await client.get("/api/agents/public")
        assert list_response.status_code == 200
        agents = list_response.json()
        public_agent = next((a for a in agents if a["id"] == agent_id), None)
        assert public_agent is not None
        assert "system_prompt" not in public_agent

    @pytest.mark.asyncio
    async def test_search_finds_matching_agents(
        self, client: AsyncClient, test_user_id: str
    ) -> None:
        """検索でマッチするエージェントが見つかる."""
        unique_name = f"SearchableAgent_{uuid4().hex[:8]}"

        # Create a public agent with unique name
        create_response = await client.post(
            "/api/agents",
            json={
                "name": unique_name,
                "description": "A searchable public agent",
                "system_prompt": "You are a helpful assistant.",
                "llm_provider": "claude",
                "llm_model": "claude-3-5-sonnet-20241022",
                "is_public": True,
            },
        )
        assert create_response.status_code == 201
        agent_id = create_response.json()["id"]

        # Search for the agent
        search_response = await client.get(
            f"/api/agents/public/search?q={unique_name[:10]}"
        )
        assert search_response.status_code == 200
        agents = search_response.json()
        assert any(a["id"] == agent_id for a in agents)

"""Personal Agent API endpoint tests."""

from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db import PersonalAgentRepository


@pytest_asyncio.fixture
async def sample_personal_agent(db_session: AsyncSession, test_user_id: UUID) -> dict:
    """Create a sample personal agent for testing."""
    repo = PersonalAgentRepository()
    agent = await repo.create(
        db_session,
        user_id=test_user_id,
        name="Test Personal Agent",
        description="A test personal agent",
        system_prompt="You are an orchestrator agent that manages other agents.",
        is_public=False,
    )

    return {
        "id": str(agent.id),
        "user_id": str(agent.user_id),
        "name": agent.name,
        "description": agent.description,
        "system_prompt": agent.system_prompt,
        "is_public": agent.is_public,
    }


@pytest_asyncio.fixture
async def other_user_personal_agent(db_session: AsyncSession) -> dict:
    """Create a personal agent owned by another user (for multi-tenant tests)."""
    other_user_id = UUID("00000000-0000-0000-0000-000000000002")
    repo = PersonalAgentRepository()
    agent = await repo.create(
        db_session,
        user_id=other_user_id,
        name="Other User's Agent",
        description="This belongs to another user",
        system_prompt="You should not be able to see this.",
        is_public=False,
    )

    return {
        "id": str(agent.id),
        "user_id": str(agent.user_id),
        "name": agent.name,
    }


@pytest.mark.asyncio
async def test_list_personal_agents_empty(client: AsyncClient):
    """Test listing personal agents when none exist."""
    response = await client.get("/api/personal-agents")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_personal_agent(client: AsyncClient):
    """Test creating a new personal agent."""
    agent_data = {
        "name": "My Personal Agent",
        "description": "An orchestrator agent",
        "system_prompt": "You manage multiple agents to accomplish tasks.",
        "is_public": False,
    }

    response = await client.post("/api/personal-agents", json=agent_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == agent_data["name"]
    assert data["description"] == agent_data["description"]
    assert data["system_prompt"] == agent_data["system_prompt"]
    assert data["is_public"] == agent_data["is_public"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_personal_agent(client: AsyncClient, sample_personal_agent: dict):
    """Test getting a personal agent by ID."""
    response = await client.get(f"/api/personal-agents/{sample_personal_agent['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sample_personal_agent["id"]
    assert data["name"] == sample_personal_agent["name"]


@pytest.mark.asyncio
async def test_get_personal_agent_not_found(client: AsyncClient):
    """Test getting a non-existent personal agent."""
    response = await client.get(
        "/api/personal-agents/00000000-0000-0000-0000-000000000999"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_personal_agent(client: AsyncClient, sample_personal_agent: dict):
    """Test updating a personal agent."""
    update_data = {
        "name": "Updated Personal Agent Name",
        "description": "Updated description",
    }

    response = await client.patch(
        f"/api/personal-agents/{sample_personal_agent['id']}",
        json=update_data,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    # Other fields should remain unchanged
    assert data["system_prompt"] == sample_personal_agent["system_prompt"]


@pytest.mark.asyncio
async def test_delete_personal_agent(client: AsyncClient, sample_personal_agent: dict):
    """Test deleting a personal agent."""
    response = await client.delete(f"/api/personal-agents/{sample_personal_agent['id']}")
    assert response.status_code == 204

    # Verify agent is deleted
    response = await client.get(f"/api/personal-agents/{sample_personal_agent['id']}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_personal_agent_validation_error(client: AsyncClient):
    """Test creating a personal agent with invalid data."""
    # Missing required fields
    agent_data = {
        "name": "Test Agent",
        # Missing system_prompt
    }

    response = await client.post("/api/personal-agents", json=agent_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_personal_agents_with_data(
    client: AsyncClient, sample_personal_agent: dict
):
    """Test listing personal agents when some exist."""
    response = await client.get("/api/personal-agents")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert any(agent["id"] == sample_personal_agent["id"] for agent in data)


# Multi-tenant isolation tests
@pytest.mark.asyncio
async def test_cannot_see_other_users_personal_agent(
    client: AsyncClient, other_user_personal_agent: dict
):
    """Test that users cannot see other users' personal agents."""
    response = await client.get(
        f"/api/personal-agents/{other_user_personal_agent['id']}"
    )
    # Should return 404 (not 403) to avoid leaking information
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_only_shows_own_personal_agents(
    client: AsyncClient,
    sample_personal_agent: dict,
    other_user_personal_agent: dict,
):
    """Test that listing only shows the current user's personal agents."""
    response = await client.get("/api/personal-agents")
    assert response.status_code == 200

    data = response.json()
    # Should include own agent
    assert any(agent["id"] == sample_personal_agent["id"] for agent in data)
    # Should NOT include other user's agent
    assert not any(agent["id"] == other_user_personal_agent["id"] for agent in data)


@pytest.mark.asyncio
async def test_cannot_update_other_users_personal_agent(
    client: AsyncClient, other_user_personal_agent: dict
):
    """Test that users cannot update other users' personal agents."""
    update_data = {"name": "Hacked!"}
    response = await client.patch(
        f"/api/personal-agents/{other_user_personal_agent['id']}",
        json=update_data,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_delete_other_users_personal_agent(
    client: AsyncClient, other_user_personal_agent: dict
):
    """Test that users cannot delete other users' personal agents."""
    response = await client.delete(
        f"/api/personal-agents/{other_user_personal_agent['id']}"
    )
    assert response.status_code == 404

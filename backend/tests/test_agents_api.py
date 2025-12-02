"""Agent API endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_agents_empty(client: AsyncClient):
    """Test listing agents when none exist."""
    response = await client.get("/api/agents")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_agent(client: AsyncClient):
    """Test creating a new agent."""
    agent_data = {
        "name": "Test Agent",
        "description": "A test agent for unit tests",
        "system_prompt": "You are a helpful assistant.",
        "llm_provider": "claude",
        "llm_model": "claude-3-5-sonnet-20241022",
        "tools": [],
        "a2a_enabled": False,
    }

    response = await client.post("/api/agents", json=agent_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == agent_data["name"]
    assert data["description"] == agent_data["description"]
    assert data["system_prompt"] == agent_data["system_prompt"]
    assert data["llm_provider"] == agent_data["llm_provider"]
    assert data["llm_model"] == agent_data["llm_model"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_agent(client: AsyncClient, sample_agent: dict):
    """Test getting an agent by ID."""
    response = await client.get(f"/api/agents/{sample_agent['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sample_agent["id"]
    assert data["name"] == sample_agent["name"]


@pytest.mark.asyncio
async def test_get_agent_not_found(client: AsyncClient):
    """Test getting a non-existent agent."""
    response = await client.get("/api/agents/00000000-0000-0000-0000-000000000999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_agent(client: AsyncClient, sample_agent: dict):
    """Test updating an agent."""
    update_data = {
        "name": "Updated Agent Name",
        "description": "Updated description",
    }

    response = await client.patch(
        f"/api/agents/{sample_agent['id']}",
        json=update_data,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    # Other fields should remain unchanged
    assert data["system_prompt"] == sample_agent["system_prompt"]


@pytest.mark.asyncio
async def test_delete_agent(client: AsyncClient, sample_agent: dict):
    """Test deleting an agent."""
    response = await client.delete(f"/api/agents/{sample_agent['id']}")
    assert response.status_code == 204

    # Verify agent is deleted
    response = await client.get(f"/api/agents/{sample_agent['id']}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_agent_validation_error(client: AsyncClient):
    """Test creating an agent with invalid data."""
    # Missing required fields
    agent_data = {
        "name": "Test Agent",
        # Missing system_prompt, llm_provider, llm_model
    }

    response = await client.post("/api/agents", json=agent_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_agents_with_data(client: AsyncClient, sample_agent: dict):
    """Test listing agents when some exist."""
    response = await client.get("/api/agents")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert any(agent["id"] == sample_agent["id"] for agent in data)

"""API endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_list_agents(client: AsyncClient):
    """Test agents list endpoint."""
    response = await client.get("/api/agents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_agent_not_implemented(client: AsyncClient):
    """Test that create agent is not yet implemented."""
    response = await client.post(
        "/api/agents",
        json={
            "name": "Test Agent",
            "system_prompt": "You are a test agent",
            "llm_provider": "claude",
            "llm_model": "claude-3-opus",
        },
    )
    assert response.status_code == 501


@pytest.mark.asyncio
async def test_a2a_agent_card_not_implemented(client: AsyncClient):
    """Test A2A agent card endpoint."""
    response = await client.get(
        "/a2a/agents/00000000-0000-0000-0000-000000000000/.well-known/agent.json"
    )
    assert response.status_code == 501


@pytest.mark.asyncio
async def test_openapi_schema(client: AsyncClient):
    """Test OpenAPI schema generation."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "Agent Platform API"

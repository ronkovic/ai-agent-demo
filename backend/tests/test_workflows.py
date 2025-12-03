"""Workflow API endpoint tests."""

from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db import WorkflowRepository


@pytest_asyncio.fixture
async def sample_workflow(db_session: AsyncSession, test_user_id: UUID) -> dict:
    """Create a sample workflow for testing."""
    repo = WorkflowRepository()
    workflow = await repo.create(
        db_session,
        user_id=test_user_id,
        name="Test Workflow",
        description="A test workflow",
        nodes=[
            {
                "id": "trigger_1",
                "type": "trigger",
                "position": {"x": 0, "y": 0},
                "data": {"trigger_type": "manual"},
            },
            {
                "id": "output_1",
                "type": "output",
                "position": {"x": 0, "y": 100},
                "data": {"output_type": "return"},
            },
        ],
        edges=[
            {
                "id": "edge_1",
                "source": "trigger_1",
                "target": "output_1",
            }
        ],
        trigger_config={},
    )

    return {
        "id": str(workflow.id),
        "user_id": str(workflow.user_id),
        "name": workflow.name,
        "description": workflow.description,
        "nodes": workflow.nodes,
        "edges": workflow.edges,
        "is_active": workflow.is_active,
    }


@pytest_asyncio.fixture
async def other_user_workflow(db_session: AsyncSession) -> dict:
    """Create a workflow owned by another user (for multi-tenant tests)."""
    other_user_id = UUID("00000000-0000-0000-0000-000000000002")
    repo = WorkflowRepository()
    workflow = await repo.create(
        db_session,
        user_id=other_user_id,
        name="Other User's Workflow",
        description="This belongs to another user",
        nodes=[],
        edges=[],
        trigger_config={},
    )

    return {
        "id": str(workflow.id),
        "user_id": str(workflow.user_id),
        "name": workflow.name,
    }


@pytest.mark.asyncio
async def test_list_workflows_empty(client: AsyncClient):
    """Test listing workflows when none exist."""
    response = await client.get("/api/workflows")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_workflow(client: AsyncClient):
    """Test creating a new workflow."""
    workflow_data = {
        "name": "My Workflow",
        "description": "A simple workflow",
        "nodes": [
            {
                "id": "trigger_1",
                "type": "trigger",
                "position": {"x": 0, "y": 0},
                "data": {"trigger_type": "manual"},
            }
        ],
        "edges": [],
        "trigger_config": {},
    }

    response = await client.post("/api/workflows", json=workflow_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == workflow_data["name"]
    assert data["description"] == workflow_data["description"]
    assert len(data["nodes"]) == 1
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_workflow(client: AsyncClient, sample_workflow: dict):
    """Test getting a workflow by ID."""
    response = await client.get(f"/api/workflows/{sample_workflow['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sample_workflow["id"]
    assert data["name"] == sample_workflow["name"]


@pytest.mark.asyncio
async def test_get_workflow_not_found(client: AsyncClient):
    """Test getting a non-existent workflow."""
    response = await client.get(
        "/api/workflows/00000000-0000-0000-0000-000000000999"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_workflow(client: AsyncClient, sample_workflow: dict):
    """Test updating a workflow."""
    update_data = {
        "name": "Updated Workflow Name",
        "description": "Updated description",
        "is_active": False,
    }

    response = await client.patch(
        f"/api/workflows/{sample_workflow['id']}",
        json=update_data,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_active"] is False
    # Other fields should remain unchanged
    assert len(data["nodes"]) == len(sample_workflow["nodes"])


@pytest.mark.asyncio
async def test_delete_workflow(client: AsyncClient, sample_workflow: dict):
    """Test deleting a workflow."""
    response = await client.delete(f"/api/workflows/{sample_workflow['id']}")
    assert response.status_code == 204

    # Verify workflow is deleted
    response = await client.get(f"/api/workflows/{sample_workflow['id']}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_workflows_with_data(
    client: AsyncClient, sample_workflow: dict
):
    """Test listing workflows when some exist."""
    response = await client.get("/api/workflows")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert any(wf["id"] == sample_workflow["id"] for wf in data)


# Multi-tenant isolation tests
@pytest.mark.asyncio
async def test_cannot_see_other_users_workflow(
    client: AsyncClient, other_user_workflow: dict
):
    """Test that users cannot see other users' workflows."""
    response = await client.get(
        f"/api/workflows/{other_user_workflow['id']}"
    )
    # Should return 404 (not 403) to avoid leaking information
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_only_shows_own_workflows(
    client: AsyncClient,
    sample_workflow: dict,
    other_user_workflow: dict,
):
    """Test that listing only shows the current user's workflows."""
    response = await client.get("/api/workflows")
    assert response.status_code == 200

    data = response.json()
    # Should include own workflow
    assert any(wf["id"] == sample_workflow["id"] for wf in data)
    # Should NOT include other user's workflow
    assert not any(wf["id"] == other_user_workflow["id"] for wf in data)


@pytest.mark.asyncio
async def test_cannot_update_other_users_workflow(
    client: AsyncClient, other_user_workflow: dict
):
    """Test that users cannot update other users' workflows."""
    update_data = {"name": "Hacked!"}
    response = await client.patch(
        f"/api/workflows/{other_user_workflow['id']}",
        json=update_data,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_delete_other_users_workflow(
    client: AsyncClient, other_user_workflow: dict
):
    """Test that users cannot delete other users' workflows."""
    response = await client.delete(
        f"/api/workflows/{other_user_workflow['id']}"
    )
    assert response.status_code == 404


# Execution tests
@pytest.mark.asyncio
async def test_execute_workflow(client: AsyncClient, sample_workflow: dict):
    """Test executing a workflow."""
    response = await client.post(
        f"/api/workflows/{sample_workflow['id']}/execute",
        json={"trigger_data": {"input": "test"}},
    )
    assert response.status_code == 202

    data = response.json()
    assert data["workflow_id"] == sample_workflow["id"]
    assert data["status"] in ["pending", "running", "completed", "failed"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_execute_workflow_without_trigger_data(
    client: AsyncClient, sample_workflow: dict
):
    """Test executing a workflow without trigger data."""
    response = await client.post(
        f"/api/workflows/{sample_workflow['id']}/execute"
    )
    assert response.status_code == 202

    data = response.json()
    assert data["workflow_id"] == sample_workflow["id"]


@pytest.mark.asyncio
async def test_list_workflow_executions(
    client: AsyncClient, sample_workflow: dict
):
    """Test listing workflow executions."""
    # First, execute the workflow
    await client.post(f"/api/workflows/{sample_workflow['id']}/execute")

    # Then, list executions
    response = await client.get(
        f"/api/workflows/{sample_workflow['id']}/executions"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_workflow_execution(
    client: AsyncClient, sample_workflow: dict
):
    """Test getting a specific workflow execution."""
    # First, execute the workflow
    exec_response = await client.post(
        f"/api/workflows/{sample_workflow['id']}/execute"
    )
    execution_id = exec_response.json()["id"]

    # Then, get the execution
    response = await client.get(
        f"/api/workflows/{sample_workflow['id']}/executions/{execution_id}"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == execution_id
    assert data["workflow_id"] == sample_workflow["id"]

"""User Settings API endpoint tests (LLM Configs and API Keys)."""

import hashlib
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db import UserApiKeyRepository, UserLLMConfigRepository


@pytest_asyncio.fixture
async def sample_llm_config(db_session: AsyncSession, test_user_id: UUID) -> dict:
    """Create a sample LLM config for testing."""
    repo = UserLLMConfigRepository()
    config = await repo.create(
        db_session,
        user_id=test_user_id,
        provider="openai",
        vault_secret_id="vault_test_secret_123",
        is_default=True,
    )

    return {
        "id": str(config.id),
        "user_id": str(config.user_id),
        "provider": config.provider,
        "is_default": config.is_default,
    }


@pytest_asyncio.fixture
async def sample_api_key(db_session: AsyncSession, test_user_id: UUID) -> dict:
    """Create a sample API key for testing."""
    repo = UserApiKeyRepository()
    raw_key = "sk_live_test1234567890abcdef"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:12] + "..."

    api_key = await repo.create(
        db_session,
        user_id=test_user_id,
        name="Test API Key",
        key_hash=key_hash,
        key_prefix=key_prefix,
        scopes=["agents:read", "agents:execute"],
        rate_limit=1000,
    )

    return {
        "id": str(api_key.id),
        "user_id": str(api_key.user_id),
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "scopes": api_key.scopes,
        "rate_limit": api_key.rate_limit,
        "raw_key": raw_key,  # For testing purposes only
    }


# LLM Config Tests
@pytest.mark.asyncio
async def test_list_llm_configs_empty(client: AsyncClient):
    """Test listing LLM configs when none exist."""
    response = await client.get("/api/user/llm-configs")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_llm_config(client: AsyncClient):
    """Test creating a new LLM config."""
    config_data = {
        "provider": "anthropic",
        "api_key": "sk-ant-test1234567890",
    }

    response = await client.post("/api/user/llm-configs", json=config_data)
    assert response.status_code == 201

    data = response.json()
    assert data["provider"] == config_data["provider"]
    assert "id" in data
    assert "api_key" not in data  # Should not expose the API key


@pytest.mark.asyncio
async def test_create_llm_config_duplicate_provider(
    client: AsyncClient, sample_llm_config: dict
):
    """Test that creating a duplicate provider config fails or updates."""
    config_data = {
        "provider": sample_llm_config["provider"],  # Same provider
        "api_key": "sk-new-key-1234567890",
    }

    response = await client.post("/api/user/llm-configs", json=config_data)
    # Should either fail (409 Conflict) or update existing
    assert response.status_code in [201, 409]


@pytest.mark.asyncio
async def test_list_llm_configs_with_data(
    client: AsyncClient, sample_llm_config: dict
):
    """Test listing LLM configs when some exist."""
    response = await client.get("/api/user/llm-configs")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert any(config["id"] == sample_llm_config["id"] for config in data)


@pytest.mark.asyncio
async def test_delete_llm_config(client: AsyncClient, sample_llm_config: dict):
    """Test deleting an LLM config."""
    response = await client.delete(f"/api/user/llm-configs/{sample_llm_config['id']}")
    assert response.status_code == 204

    # Verify config is deleted
    response = await client.get("/api/user/llm-configs")
    data = response.json()
    assert not any(config["id"] == sample_llm_config["id"] for config in data)


@pytest.mark.asyncio
async def test_delete_llm_config_not_found(client: AsyncClient):
    """Test deleting a non-existent LLM config."""
    response = await client.delete(
        "/api/user/llm-configs/00000000-0000-0000-0000-000000000999"
    )
    assert response.status_code == 404


# API Key Tests
@pytest.mark.asyncio
async def test_list_api_keys_empty(client: AsyncClient):
    """Test listing API keys when none exist."""
    response = await client.get("/api/user/api-keys")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_api_key(client: AsyncClient):
    """Test creating a new API key."""
    key_data = {
        "name": "My Production Key",
        "scopes": ["agents:read"],
        "rate_limit": 500,
    }

    response = await client.post("/api/user/api-keys", json=key_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == key_data["name"]
    assert data["scopes"] == key_data["scopes"]
    assert data["rate_limit"] == key_data["rate_limit"]
    assert "id" in data
    assert "key" in data  # Should include the raw key on creation
    assert data["key"].startswith("sk_live_")  # Key format
    assert "key_prefix" in data


@pytest.mark.asyncio
async def test_create_api_key_default_rate_limit(client: AsyncClient):
    """Test creating an API key with default rate limit."""
    key_data = {
        "name": "Default Rate Key",
        "scopes": [],
    }

    response = await client.post("/api/user/api-keys", json=key_data)
    assert response.status_code == 201

    data = response.json()
    assert data["rate_limit"] == 1000  # Default value


@pytest.mark.asyncio
async def test_list_api_keys_with_data(client: AsyncClient, sample_api_key: dict):
    """Test listing API keys when some exist."""
    response = await client.get("/api/user/api-keys")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    # Find our key
    our_key = next((k for k in data if k["id"] == sample_api_key["id"]), None)
    assert our_key is not None
    assert our_key["name"] == sample_api_key["name"]
    assert our_key["key_prefix"] == sample_api_key["key_prefix"]
    # Should NOT include raw key in list
    assert "key" not in our_key or our_key.get("key") is None


@pytest.mark.asyncio
async def test_delete_api_key(client: AsyncClient, sample_api_key: dict):
    """Test deleting an API key."""
    response = await client.delete(f"/api/user/api-keys/{sample_api_key['id']}")
    assert response.status_code == 204

    # Verify key is deleted
    response = await client.get("/api/user/api-keys")
    data = response.json()
    assert not any(key["id"] == sample_api_key["id"] for key in data)


@pytest.mark.asyncio
async def test_delete_api_key_not_found(client: AsyncClient):
    """Test deleting a non-existent API key."""
    response = await client.delete(
        "/api/user/api-keys/00000000-0000-0000-0000-000000000999"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_api_key_hash_is_sha256(client: AsyncClient, db_session: AsyncSession):
    """Test that API keys are properly hashed with SHA-256."""
    key_data = {
        "name": "Hash Test Key",
        "scopes": [],
    }

    response = await client.post("/api/user/api-keys", json=key_data)
    assert response.status_code == 201

    data = response.json()
    raw_key = data["key"]

    # Verify the hash matches
    expected_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    # Check in database
    repo = UserApiKeyRepository()
    api_key = await repo.get_by_hash(db_session, expected_hash)
    assert api_key is not None
    assert api_key.key_hash == expected_hash


# Validation Tests
@pytest.mark.asyncio
async def test_create_llm_config_missing_provider(client: AsyncClient):
    """Test creating LLM config without provider fails."""
    config_data = {
        "api_key": "sk-test-key",
        # Missing provider
    }

    response = await client.post("/api/user/llm-configs", json=config_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_api_key_missing_name(client: AsyncClient):
    """Test creating API key without name fails."""
    key_data = {
        "scopes": ["agents:read"],
        # Missing name
    }

    response = await client.post("/api/user/api-keys", json=key_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_llm_config_invalid_provider(client: AsyncClient):
    """Test creating LLM config with invalid provider."""
    config_data = {
        "provider": "invalid_provider",
        "api_key": "sk-test-key",
    }

    response = await client.post("/api/user/llm-configs", json=config_data)
    # Should fail validation (422) or be accepted depending on implementation
    # For now, we allow any string but may want to restrict in the future
    assert response.status_code in [201, 422]

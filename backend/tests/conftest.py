"""Pytest configuration and fixtures."""

import os
from collections.abc import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from agent_platform.api.deps import get_current_user_id
from agent_platform.db.models import Base
from agent_platform.db.session import get_db
from agent_platform.main import app

# Test database URL - default to SQLite in-memory for CI/testing
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///:memory:",
)


@pytest_asyncio.fixture
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create async engine for tests."""
    # SQLite doesn't support pool options
    is_sqlite = TEST_DATABASE_URL.startswith("sqlite")

    if is_sqlite:
        engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    else:
        engine = create_async_engine(
            TEST_DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

    # Create all tables for testing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests.

    Each test gets a fresh session with a transaction that is
    rolled back after the test completes.
    """
    async_session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        async with session.begin():
            yield session
            # Rollback happens automatically when exiting begin() context
            # after session is closed without commit


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession, test_user_id: UUID
) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with database session and auth override."""

    async def override_get_db():
        yield db_session

    async def override_get_current_user_id():
        return test_user_id

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_id() -> UUID:
    """Get test user ID."""
    return UUID("00000000-0000-0000-0000-000000000001")


@pytest_asyncio.fixture
async def sample_agent(db_session: AsyncSession, test_user_id: UUID) -> dict:
    """Create a sample agent for testing."""
    from agent_platform.db import AgentRepository

    repo = AgentRepository()
    agent = await repo.create(
        db_session,
        user_id=test_user_id,
        name="Test Agent",
        description="A test agent",
        system_prompt="You are a helpful test assistant.",
        llm_provider="claude",
        llm_model="claude-3-5-sonnet-20241022",
        tools=[],
        a2a_enabled=False,
    )

    return {
        "id": str(agent.id),
        "user_id": str(agent.user_id),
        "name": agent.name,
        "description": agent.description,
        "system_prompt": agent.system_prompt,
        "llm_provider": agent.llm_provider,
        "llm_model": agent.llm_model,
        "tools": agent.tools,
        "a2a_enabled": agent.a2a_enabled,
    }

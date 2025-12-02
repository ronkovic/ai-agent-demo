"""Pytest configuration and fixtures."""

import pytest
from httpx import ASGITransport, AsyncClient

from agent_platform.main import app


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

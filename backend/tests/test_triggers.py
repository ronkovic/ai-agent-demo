"""Tests for trigger models and API endpoints."""

import hashlib
import hmac
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.api.deps import get_db
from agent_platform.db.models import ScheduleTrigger, WebhookTrigger, Workflow
from agent_platform.main import app


@pytest_asyncio.fixture
async def test_workflow(db_session: AsyncSession, test_user_id: UUID):
    """Create a test workflow."""
    workflow = Workflow(
        id=uuid4(),
        user_id=str(test_user_id),
        name="Test Workflow",
        description="Test workflow for triggers",
        nodes=[],
        edges=[],
        trigger_config={},
        is_active=True,
    )
    db_session.add(workflow)
    await db_session.flush()
    await db_session.refresh(workflow)
    return workflow


@pytest_asyncio.fixture
async def schedule_trigger(db_session: AsyncSession, test_workflow: Workflow):
    """Create a test schedule trigger."""
    trigger = ScheduleTrigger(
        id=uuid4(),
        workflow_id=test_workflow.id,
        cron_expression="0 9 * * *",
        timezone="UTC",
        is_active=True,
        next_run_at=datetime(2025, 1, 1, 9, 0, 0, tzinfo=UTC),
    )
    db_session.add(trigger)
    await db_session.flush()
    await db_session.refresh(trigger)
    return trigger


@pytest_asyncio.fixture
async def webhook_trigger(db_session: AsyncSession, test_workflow: Workflow):
    """Create a test webhook trigger."""
    trigger = WebhookTrigger(
        id=uuid4(),
        workflow_id=test_workflow.id,
        webhook_path=f"test-webhook-{uuid4().hex[:8]}",
        secret="test-secret-key",
        is_active=True,
    )
    db_session.add(trigger)
    await db_session.flush()
    await db_session.refresh(trigger)
    return trigger


class TestScheduleTriggerModel:
    """Tests for ScheduleTrigger model."""

    @pytest.mark.asyncio
    async def test_create_schedule_trigger(self, db_session: AsyncSession, test_workflow: Workflow):
        """Test creating a schedule trigger."""
        trigger = ScheduleTrigger(
            id=uuid4(),
            workflow_id=test_workflow.id,
            cron_expression="0 12 * * *",
            timezone="Asia/Tokyo",
            is_active=True,
        )
        db_session.add(trigger)
        await db_session.flush()
        await db_session.refresh(trigger)

        assert trigger.id is not None
        assert trigger.cron_expression == "0 12 * * *"
        assert trigger.timezone == "Asia/Tokyo"
        assert trigger.is_active is True
        assert trigger.created_at is not None

    @pytest.mark.asyncio
    async def test_schedule_trigger_relationship(
        self, db_session: AsyncSession, schedule_trigger: ScheduleTrigger, test_workflow: Workflow
    ):
        """Test schedule trigger has correct workflow relationship."""
        await db_session.refresh(schedule_trigger, ["workflow"])
        assert schedule_trigger.workflow_id == test_workflow.id
        assert schedule_trigger.workflow is not None
        assert schedule_trigger.workflow.id == test_workflow.id


class TestWebhookTriggerModel:
    """Tests for WebhookTrigger model."""

    @pytest.mark.asyncio
    async def test_create_webhook_trigger(self, db_session: AsyncSession, test_workflow: Workflow):
        """Test creating a webhook trigger."""
        trigger = WebhookTrigger(
            id=uuid4(),
            workflow_id=test_workflow.id,
            webhook_path=f"my-custom-hook-{uuid4().hex[:8]}",
            secret="my-secret-key",
            is_active=True,
        )
        db_session.add(trigger)
        await db_session.flush()
        await db_session.refresh(trigger)

        assert trigger.id is not None
        assert "my-custom-hook" in trigger.webhook_path
        assert trigger.secret == "my-secret-key"
        assert trigger.is_active is True


class TestHMACSignatureVerification:
    """Tests for HMAC signature verification."""

    def test_verify_valid_signature(self):
        """Test HMAC signature verification with valid signature."""
        from agent_platform.api.routes.webhooks import verify_hmac_signature

        secret = "test-secret"
        payload = b'{"event": "test"}'
        expected_sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        signature = f"sha256={expected_sig}"

        assert verify_hmac_signature(payload, signature, secret) is True

    def test_verify_invalid_signature(self):
        """Test HMAC signature verification with invalid signature."""
        from agent_platform.api.routes.webhooks import verify_hmac_signature

        secret = "test-secret"
        payload = b'{"event": "test"}'
        signature = "sha256=invalid-signature"

        assert verify_hmac_signature(payload, signature, secret) is False

    def test_verify_wrong_secret(self):
        """Test HMAC signature verification with wrong secret."""
        from agent_platform.api.routes.webhooks import verify_hmac_signature

        correct_secret = "correct-secret"
        wrong_secret = "wrong-secret"
        payload = b'{"event": "test"}'
        sig = hmac.new(correct_secret.encode(), payload, hashlib.sha256).hexdigest()
        signature = f"sha256={sig}"

        assert verify_hmac_signature(payload, signature, wrong_secret) is False


class TestScheduleTriggerAPI:
    """Tests for Schedule Trigger API endpoints."""

    @pytest.mark.asyncio
    async def test_list_schedule_triggers(
        self, client: AsyncClient, test_workflow: Workflow, schedule_trigger: ScheduleTrigger
    ):
        """Test listing schedule triggers for a workflow."""
        response = await client.get(
            f"/api/workflows/{test_workflow.id}/triggers/schedules"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(t["id"] == str(schedule_trigger.id) for t in data)

    @pytest.mark.asyncio
    async def test_create_schedule_trigger(self, client: AsyncClient, test_workflow: Workflow):
        """Test creating a schedule trigger."""
        response = await client.post(
            f"/api/workflows/{test_workflow.id}/triggers/schedules",
            json={"cron_expression": "0 18 * * *"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["cron_expression"] == "0 18 * * *"
        assert data["is_active"] is True
        assert data["workflow_id"] == str(test_workflow.id)

    @pytest.mark.asyncio
    async def test_create_schedule_trigger_invalid_cron(
        self, client: AsyncClient, test_workflow: Workflow
    ):
        """Test creating a schedule trigger with invalid cron expression."""
        response = await client.post(
            f"/api/workflows/{test_workflow.id}/triggers/schedules",
            json={"cron_expression": "invalid"},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_schedule_trigger(
        self, client: AsyncClient, test_workflow: Workflow, schedule_trigger: ScheduleTrigger
    ):
        """Test deleting a schedule trigger."""
        response = await client.delete(
            f"/api/workflows/{test_workflow.id}/triggers/schedules/{schedule_trigger.id}"
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_toggle_schedule_trigger(
        self, client: AsyncClient, test_workflow: Workflow, schedule_trigger: ScheduleTrigger
    ):
        """Test toggling a schedule trigger."""
        response = await client.patch(
            f"/api/workflows/{test_workflow.id}/triggers/schedules/{schedule_trigger.id}/toggle",
            json={"is_active": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False


class TestWebhookTriggerAPI:
    """Tests for Webhook Trigger API endpoints."""

    @pytest.mark.asyncio
    async def test_list_webhook_triggers(
        self, client: AsyncClient, test_workflow: Workflow, webhook_trigger: WebhookTrigger
    ):
        """Test listing webhook triggers for a workflow."""
        response = await client.get(
            f"/api/workflows/{test_workflow.id}/triggers/webhooks"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_create_webhook_trigger(self, client: AsyncClient, test_workflow: Workflow):
        """Test creating a webhook trigger."""
        webhook_path = f"new-webhook-{uuid4().hex[:8]}"
        response = await client.post(
            f"/api/workflows/{test_workflow.id}/triggers/webhooks",
            json={"webhook_path": webhook_path},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["webhook_path"] == webhook_path
        assert data["secret"] is not None  # Secret is returned on creation
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_duplicate_webhook_path(
        self, client: AsyncClient, test_workflow: Workflow, webhook_trigger: WebhookTrigger
    ):
        """Test creating webhook with duplicate path fails."""
        response = await client.post(
            f"/api/workflows/{test_workflow.id}/triggers/webhooks",
            json={"webhook_path": webhook_trigger.webhook_path},
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_delete_webhook_trigger(
        self, client: AsyncClient, test_workflow: Workflow, webhook_trigger: WebhookTrigger
    ):
        """Test deleting a webhook trigger."""
        response = await client.delete(
            f"/api/workflows/{test_workflow.id}/triggers/webhooks/{webhook_trigger.id}"
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_regenerate_webhook_secret(
        self, client: AsyncClient, test_workflow: Workflow, webhook_trigger: WebhookTrigger
    ):
        """Test regenerating webhook secret."""
        old_secret = webhook_trigger.secret

        response = await client.post(
            f"/api/workflows/{test_workflow.id}/triggers/webhooks/{webhook_trigger.id}/regenerate-secret"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["secret"] is not None
        assert data["secret"] != old_secret


class TestWebhookEndpoint:
    """Tests for the webhook receiver endpoint."""

    @pytest.mark.asyncio
    async def test_webhook_not_found(self, db_session: AsyncSession):
        """Test webhook endpoint with non-existent path."""

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post(
                    "/webhooks/non-existent-webhook",
                    json={"event": "test"},
                )

            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_webhook_without_signature(
        self, db_session: AsyncSession, webhook_trigger: WebhookTrigger
    ):
        """Test webhook endpoint without signature (if secret is set, should fail)."""

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post(
                    f"/webhooks/{webhook_trigger.webhook_path}",
                    json={"event": "test"},
                )

            # Should fail because webhook has a secret but no signature provided
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

"""Trigger management API endpoints."""

import secrets
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.core.config import settings
from agent_platform.db import (
    ScheduleTriggerRepository,
    WebhookTriggerRepository,
    WorkflowRepository,
)
from agent_platform.tasks.scheduler import get_next_run_time, validate_cron_expression

from ..deps import get_current_user_id, get_db

router = APIRouter()


# =============================================================================
# Pydantic Models - Schedule Trigger
# =============================================================================


class ScheduleTriggerCreate(BaseModel):
    """スケジュールトリガー作成リクエスト."""

    cron_expression: str = Field(..., description="cron式 (例: '0 9 * * *')")
    timezone: str = Field(default="UTC", description="タイムゾーン")


class ScheduleTriggerResponse(BaseModel):
    """スケジュールトリガーレスポンス."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    cron_expression: str
    timezone: str
    is_active: bool
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime


class ScheduleTriggerToggle(BaseModel):
    """スケジュールトリガー有効/無効切り替え."""

    is_active: bool


# =============================================================================
# Pydantic Models - Webhook Trigger
# =============================================================================


class WebhookTriggerCreate(BaseModel):
    """Webhookトリガー作成リクエスト."""

    webhook_path: str = Field(..., description="Webhookパス (例: 'my-workflow-hook')")


class WebhookTriggerResponse(BaseModel):
    """Webhookトリガーレスポンス."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    webhook_path: str
    secret: str | None  # 作成時のみ返す
    is_active: bool
    last_triggered_at: datetime | None
    created_at: datetime
    webhook_url: str  # フルURL


class WebhookTriggerSecretResponse(BaseModel):
    """Webhookシークレット再生成レスポンス."""

    secret: str


# =============================================================================
# Helper Functions
# =============================================================================


def generate_webhook_secret() -> str:
    """Webhookシークレットを生成."""
    return secrets.token_urlsafe(32)


def build_webhook_url(webhook_path: str) -> str:
    """Webhook URLを構築."""
    base_url = settings.a2a_base_url.rstrip("/")
    return f"{base_url}/webhooks/{webhook_path}"


# =============================================================================
# Schedule Trigger Endpoints
# =============================================================================


@router.get("/schedules", response_model=list[ScheduleTriggerResponse])
async def list_schedule_triggers(
    workflow_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[ScheduleTriggerResponse]:
    """ワークフローのスケジュールトリガー一覧を取得."""
    # ワークフロー所有権確認
    workflow_repo = WorkflowRepository()
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    trigger_repo = ScheduleTriggerRepository()
    triggers = await trigger_repo.list_by_workflow(db, workflow_id)
    return [ScheduleTriggerResponse.model_validate(t) for t in triggers]


@router.post(
    "/schedules",
    response_model=ScheduleTriggerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule_trigger(
    workflow_id: UUID,
    request: ScheduleTriggerCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ScheduleTriggerResponse:
    """スケジュールトリガーを作成."""
    # ワークフロー所有権確認
    workflow_repo = WorkflowRepository()
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # cron式バリデーション
    if not validate_cron_expression(request.cron_expression):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid cron expression",
        )

    # 次回実行時刻計算
    next_run = get_next_run_time(request.cron_expression)

    trigger_repo = ScheduleTriggerRepository()
    trigger = await trigger_repo.create(
        db,
        workflow_id=workflow_id,
        cron_expression=request.cron_expression,
        timezone=request.timezone,
    )
    trigger.next_run_at = next_run
    await db.commit()

    return ScheduleTriggerResponse.model_validate(trigger)


@router.delete("/schedules/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule_trigger(
    workflow_id: UUID,
    trigger_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """スケジュールトリガーを削除."""
    # ワークフロー所有権確認
    workflow_repo = WorkflowRepository()
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    trigger_repo = ScheduleTriggerRepository()
    trigger = await trigger_repo.get(db, trigger_id)
    if not trigger or trigger.workflow_id != workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger not found",
        )

    await trigger_repo.delete(db, trigger)
    await db.commit()


@router.patch("/schedules/{trigger_id}/toggle", response_model=ScheduleTriggerResponse)
async def toggle_schedule_trigger(
    workflow_id: UUID,
    trigger_id: UUID,
    request: ScheduleTriggerToggle,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ScheduleTriggerResponse:
    """スケジュールトリガーの有効/無効を切り替え."""
    # ワークフロー所有権確認
    workflow_repo = WorkflowRepository()
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    trigger_repo = ScheduleTriggerRepository()
    trigger = await trigger_repo.get(db, trigger_id)
    if not trigger or trigger.workflow_id != workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger not found",
        )

    trigger = await trigger_repo.update(db, trigger, is_active=request.is_active)

    # 有効化時は次回実行時刻を更新
    if request.is_active:
        trigger.next_run_at = get_next_run_time(trigger.cron_expression)

    await db.commit()
    return ScheduleTriggerResponse.model_validate(trigger)


# =============================================================================
# Webhook Trigger Endpoints
# =============================================================================


@router.get("/webhooks", response_model=list[WebhookTriggerResponse])
async def list_webhook_triggers(
    workflow_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[WebhookTriggerResponse]:
    """ワークフローのWebhookトリガー一覧を取得."""
    # ワークフロー所有権確認
    workflow_repo = WorkflowRepository()
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    trigger_repo = WebhookTriggerRepository()
    triggers = await trigger_repo.list_by_workflow(db, workflow_id)

    return [
        WebhookTriggerResponse(
            id=t.id,
            workflow_id=t.workflow_id,
            webhook_path=t.webhook_path,
            secret=None,  # 一覧では表示しない
            is_active=t.is_active,
            last_triggered_at=t.last_triggered_at,
            created_at=t.created_at,
            webhook_url=build_webhook_url(t.webhook_path),
        )
        for t in triggers
    ]


@router.post(
    "/webhooks",
    response_model=WebhookTriggerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_webhook_trigger(
    workflow_id: UUID,
    request: WebhookTriggerCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> WebhookTriggerResponse:
    """Webhookトリガーを作成."""
    # ワークフロー所有権確認
    workflow_repo = WorkflowRepository()
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # シークレット生成
    secret = generate_webhook_secret()

    trigger_repo = WebhookTriggerRepository()

    # パス重複チェック
    existing = await trigger_repo.get_by_path(db, request.webhook_path)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Webhook path already exists",
        )

    trigger = await trigger_repo.create(
        db,
        workflow_id=workflow_id,
        webhook_path=request.webhook_path,
        secret=secret,
    )
    await db.commit()

    return WebhookTriggerResponse(
        id=trigger.id,
        workflow_id=trigger.workflow_id,
        webhook_path=trigger.webhook_path,
        secret=secret,  # 作成時のみ表示
        is_active=trigger.is_active,
        last_triggered_at=trigger.last_triggered_at,
        created_at=trigger.created_at,
        webhook_url=build_webhook_url(trigger.webhook_path),
    )


@router.delete("/webhooks/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook_trigger(
    workflow_id: UUID,
    trigger_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Webhookトリガーを削除."""
    # ワークフロー所有権確認
    workflow_repo = WorkflowRepository()
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    trigger_repo = WebhookTriggerRepository()
    trigger = await trigger_repo.get(db, trigger_id)
    if not trigger or trigger.workflow_id != workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger not found",
        )

    await trigger_repo.delete(db, trigger)
    await db.commit()


@router.post(
    "/webhooks/{trigger_id}/regenerate-secret",
    response_model=WebhookTriggerSecretResponse,
)
async def regenerate_webhook_secret(
    workflow_id: UUID,
    trigger_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> WebhookTriggerSecretResponse:
    """Webhookシークレットを再生成."""
    # ワークフロー所有権確認
    workflow_repo = WorkflowRepository()
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    trigger_repo = WebhookTriggerRepository()
    trigger = await trigger_repo.get(db, trigger_id)
    if not trigger or trigger.workflow_id != workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger not found",
        )

    # 新しいシークレット生成
    new_secret = generate_webhook_secret()
    await trigger_repo.update(db, trigger, secret=new_secret)
    await db.commit()

    return WebhookTriggerSecretResponse(secret=new_secret)

"""Webhook API endpoints for triggering workflows."""

import hashlib
import hmac
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db import WebhookTriggerRepository
from agent_platform.tasks import execute_workflow_task

from ..deps import get_db

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================


class WebhookResponse(BaseModel):
    """Webhook実行レスポンス."""

    status: str
    task_id: str
    workflow_id: str


class WebhookErrorResponse(BaseModel):
    """Webhookエラーレスポンス."""

    detail: str


# =============================================================================
# Helper Functions
# =============================================================================


def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    """HMAC-SHA256署名を検証.

    Args:
        payload: リクエストボディ
        signature: X-Webhook-Signature ヘッダー値
        secret: Webhookシークレット

    Returns:
        署名が有効ならTrue
    """
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/{webhook_path:path}",
    response_model=WebhookResponse,
    responses={
        401: {"model": WebhookErrorResponse},
        404: {"model": WebhookErrorResponse},
    },
)
async def handle_webhook(
    webhook_path: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    """Webhookリクエストを受信してワークフロー実行.

    - HMAC署名が設定されている場合は検証を行う
    - ワークフローを非同期タスクとして実行
    """
    webhook_repo = WebhookTriggerRepository()
    trigger = await webhook_repo.get_by_path(db, webhook_path)

    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )

    # HMAC署名検証
    if trigger.secret:
        signature = request.headers.get("X-Webhook-Signature", "")
        payload = await request.body()
        if not verify_hmac_signature(payload, signature, trigger.secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature",
            )

    # ペイロード取得
    try:
        body = await request.json()
    except Exception:
        body = {}

    # last_triggered_at 更新
    trigger.last_triggered_at = datetime.now(UTC)
    await db.commit()

    # 非同期タスクとして実行
    task = execute_workflow_task.delay(
        workflow_id=str(trigger.workflow_id),
        trigger_type="webhook",
        trigger_data={
            "webhook_path": webhook_path,
            "headers": dict(request.headers),
            "body": body,
        },
    )

    return WebhookResponse(
        status="accepted",
        task_id=task.id,
        workflow_id=str(trigger.workflow_id),
    )

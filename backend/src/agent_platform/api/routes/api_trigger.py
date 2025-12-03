"""API Trigger endpoints for authenticated workflow execution."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db import UserApiKey, WorkflowRepository
from agent_platform.services.rate_limiter import get_rate_limit_key, rate_limiter
from agent_platform.tasks import execute_workflow_task

from ..deps import get_db, verify_api_key

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================


class ApiTriggerRequest(BaseModel):
    """API Trigger リクエスト."""

    trigger_data: dict[str, Any] | None = None


class ApiTriggerResponse(BaseModel):
    """API Trigger レスポンス."""

    status: str
    task_id: str
    workflow_id: str
    rate_limit_remaining: int


class ApiTriggerErrorResponse(BaseModel):
    """API Trigger エラーレスポンス."""

    detail: str


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/execute/{workflow_id}",
    response_model=ApiTriggerResponse,
    responses={
        401: {"model": ApiTriggerErrorResponse},
        403: {"model": ApiTriggerErrorResponse},
        404: {"model": ApiTriggerErrorResponse},
        429: {"model": ApiTriggerErrorResponse},
    },
)
async def api_execute_workflow(
    workflow_id: UUID,
    request: ApiTriggerRequest | None = None,
    api_key: UserApiKey = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiTriggerResponse:
    """APIキー認証でワークフロー実行.

    - X-API-Key ヘッダーでAPIキーを渡す
    - Rate Limiting が適用される
    - スコープ "workflows:execute" または "*" が必要
    """
    # スコープチェック
    if "workflows:execute" not in api_key.scopes and "*" not in api_key.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient scope",
        )

    # ワークフロー取得（同じユーザーのもののみ）
    workflow_repo = WorkflowRepository()
    workflow = await workflow_repo.get_by_user(db, workflow_id, api_key.user_id)

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # アクティブチェック
    if not workflow.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is not active",
        )

    # 残りリクエスト数取得
    rate_key = get_rate_limit_key(api_key.id)
    remaining = await rate_limiter.get_remaining(rate_key, api_key.rate_limit)

    # 非同期タスク実行
    trigger_data = request.trigger_data if request else None
    task = execute_workflow_task.delay(
        workflow_id=str(workflow_id),
        trigger_type="api",
        trigger_data={
            "api_key_id": str(api_key.id),
            **(trigger_data or {}),
        },
    )

    return ApiTriggerResponse(
        status="accepted",
        task_id=task.id,
        workflow_id=str(workflow_id),
        rate_limit_remaining=remaining,
    )


@router.get("/rate-limit")
async def get_rate_limit_status(
    api_key: UserApiKey = Depends(verify_api_key),
) -> dict:
    """現在のRate Limit状態を取得."""
    rate_key = get_rate_limit_key(api_key.id)
    remaining = await rate_limiter.get_remaining(rate_key, api_key.rate_limit)

    return {
        "limit": api_key.rate_limit,
        "remaining": remaining,
        "reset_window_seconds": 3600,
    }

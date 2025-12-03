"""Workflow管理API."""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import WorkflowExecutionRepository, WorkflowRepository
from ..deps import get_current_user_id, get_db, get_workflow_execution_repo, get_workflow_repo

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================


class NodePosition(BaseModel):
    """ノード位置."""

    x: float
    y: float


class WorkflowNode(BaseModel):
    """ワークフローノード."""

    id: str
    type: str  # trigger, agent, condition, transform, tool, output
    position: NodePosition
    data: dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    """ワークフローエッジ."""

    id: str
    source: str
    target: str
    sourceHandle: str | None = None  # noqa: N815
    targetHandle: str | None = None  # noqa: N815


class WorkflowCreate(BaseModel):
    """Workflow作成リクエスト."""

    name: str
    description: str | None = None
    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)
    trigger_config: dict[str, Any] = Field(default_factory=dict)


class WorkflowUpdate(BaseModel):
    """Workflow更新リクエスト."""

    name: str | None = None
    description: str | None = None
    nodes: list[WorkflowNode] | None = None
    edges: list[WorkflowEdge] | None = None
    trigger_config: dict[str, Any] | None = None
    is_active: bool | None = None


class WorkflowResponse(BaseModel):
    """Workflowレスポンス."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    trigger_config: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class WorkflowExecutionCreate(BaseModel):
    """Workflow実行リクエスト."""

    trigger_data: dict[str, Any] | None = None


class WorkflowExecutionResponse(BaseModel):
    """Workflow実行レスポンス."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    status: str
    trigger_data: dict[str, Any] | None
    node_results: dict[str, Any]
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


# =============================================================================
# Workflow CRUD Endpoints
# =============================================================================


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: WorkflowRepository = Depends(get_workflow_repo),
) -> list[WorkflowResponse]:
    """Workflow一覧取得."""
    workflows = await repo.list_by_user(db, user_id)
    return [WorkflowResponse.model_validate(w) for w in workflows]


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: WorkflowRepository = Depends(get_workflow_repo),
) -> WorkflowResponse:
    """Workflow作成."""
    workflow = await repo.create(
        db,
        user_id=user_id,
        name=workflow_data.name,
        description=workflow_data.description,
        nodes=[n.model_dump() for n in workflow_data.nodes],
        edges=[e.model_dump() for e in workflow_data.edges],
        trigger_config=workflow_data.trigger_config,
    )
    return WorkflowResponse.model_validate(workflow)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: WorkflowRepository = Depends(get_workflow_repo),
) -> WorkflowResponse:
    """Workflow取得."""
    workflow = await repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )
    return WorkflowResponse.model_validate(workflow)


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: WorkflowRepository = Depends(get_workflow_repo),
) -> WorkflowResponse:
    """Workflow更新."""
    workflow = await repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Build update dict
    update_data: dict[str, Any] = {}
    if workflow_data.name is not None:
        update_data["name"] = workflow_data.name
    if workflow_data.description is not None:
        update_data["description"] = workflow_data.description
    if workflow_data.nodes is not None:
        update_data["nodes"] = [n.model_dump() for n in workflow_data.nodes]
    if workflow_data.edges is not None:
        update_data["edges"] = [e.model_dump() for e in workflow_data.edges]
    if workflow_data.trigger_config is not None:
        update_data["trigger_config"] = workflow_data.trigger_config
    if workflow_data.is_active is not None:
        update_data["is_active"] = workflow_data.is_active

    workflow = await repo.update(db, workflow, **update_data)
    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    repo: WorkflowRepository = Depends(get_workflow_repo),
) -> None:
    """Workflow削除."""
    workflow = await repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )
    await repo.delete(db, workflow)


# =============================================================================
# Workflow Execution Endpoints
# =============================================================================


@router.post(
    "/{workflow_id}/execute",
    response_model=WorkflowExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def execute_workflow(
    workflow_id: UUID,
    background_tasks: BackgroundTasks,
    execution_data: WorkflowExecutionCreate | None = None,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    workflow_repo: WorkflowRepository = Depends(get_workflow_repo),
    execution_repo: WorkflowExecutionRepository = Depends(get_workflow_execution_repo),
) -> WorkflowExecutionResponse:
    """Workflow実行.

    ワークフローを非同期で実行し、実行レコードを返す。
    """
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    trigger_data = execution_data.trigger_data if execution_data else None

    # WorkflowEngineで実行
    from ...services.workflow_engine import WorkflowEngine

    engine = WorkflowEngine(db, execution_repo)
    execution = await engine.execute(workflow, trigger_data)

    return WorkflowExecutionResponse.model_validate(execution)


@router.get("/{workflow_id}/executions", response_model=list[WorkflowExecutionResponse])
async def list_workflow_executions(
    workflow_id: UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    workflow_repo: WorkflowRepository = Depends(get_workflow_repo),
    execution_repo: WorkflowExecutionRepository = Depends(get_workflow_execution_repo),
) -> list[WorkflowExecutionResponse]:
    """Workflow実行履歴取得."""
    # Verify user owns the workflow
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    executions = await execution_repo.list_by_workflow(db, workflow_id, limit=limit)
    return [WorkflowExecutionResponse.model_validate(e) for e in executions]


@router.get(
    "/{workflow_id}/executions/{execution_id}",
    response_model=WorkflowExecutionResponse,
)
async def get_workflow_execution(
    workflow_id: UUID,
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    workflow_repo: WorkflowRepository = Depends(get_workflow_repo),
    execution_repo: WorkflowExecutionRepository = Depends(get_workflow_execution_repo),
) -> WorkflowExecutionResponse:
    """Workflow実行詳細取得."""
    # Verify user owns the workflow
    workflow = await workflow_repo.get_by_user(db, workflow_id, user_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    execution = await execution_repo.get(db, execution_id)
    if not execution or execution.workflow_id != workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found",
        )

    return WorkflowExecutionResponse.model_validate(execution)

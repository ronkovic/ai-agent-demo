"""Celery tasks for workflow execution."""

import asyncio
from datetime import UTC, datetime
from uuid import UUID

from agent_platform.db import (
    AsyncSessionLocal,
    ScheduleTriggerRepository,
    Workflow,
    WorkflowRepository,
)
from agent_platform.services.workflow_engine import WorkflowEngine
from agent_platform.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def execute_workflow_task(
    self,
    workflow_id: str,
    trigger_type: str,
    trigger_data: dict | None = None,
) -> dict:
    """ワークフロー非同期実行タスク.

    Args:
        self: Celeryタスクインスタンス
        workflow_id: ワークフローID
        trigger_type: トリガー種別 (schedule, webhook, api)
        trigger_data: トリガーデータ

    Returns:
        実行結果
    """

    async def _execute() -> dict:
        async with AsyncSessionLocal() as db:
            repo = WorkflowRepository()
            workflow = await repo.get(db, UUID(workflow_id))
            if not workflow:
                raise ValueError(f"Workflow not found: {workflow_id}")

            engine = WorkflowEngine(db)
            execution = await engine.execute(
                workflow,
                trigger_data={
                    "trigger_type": trigger_type,
                    **(trigger_data or {}),
                },
            )
            await db.commit()
            return {
                "execution_id": str(execution.id),
                "status": execution.status,
            }

    return asyncio.run(_execute())


@celery_app.task
def scheduled_workflow_trigger(schedule_trigger_id: str) -> dict:
    """スケジュールトリガーからのワークフロー実行.

    Args:
        schedule_trigger_id: スケジュールトリガーID

    Returns:
        実行結果
    """

    async def _execute() -> dict:
        async with AsyncSessionLocal() as db:
            trigger_repo = ScheduleTriggerRepository()
            trigger = await trigger_repo.get(db, UUID(schedule_trigger_id))

            if not trigger or not trigger.is_active:
                return {"status": "skipped", "reason": "trigger inactive"}

            # ワークフロー取得
            workflow_repo = WorkflowRepository()
            workflow: Workflow | None = await workflow_repo.get(db, trigger.workflow_id)
            if not workflow:
                return {"status": "skipped", "reason": "workflow not found"}

            # last_run_at 更新
            trigger.last_run_at = datetime.now(UTC)
            await db.flush()

            # ワークフロー実行
            engine = WorkflowEngine(db)
            execution = await engine.execute(
                workflow,
                trigger_data={
                    "trigger_type": "schedule",
                    "schedule_trigger_id": str(trigger.id),
                },
            )
            await db.commit()
            return {
                "execution_id": str(execution.id),
                "status": execution.status,
            }

    return asyncio.run(_execute())


@celery_app.task
def sync_schedule_triggers_task() -> dict:
    """スケジュールトリガーを同期するタスク.

    定期的に実行してDBのトリガーとCelery Beatを同期する.
    """
    from agent_platform.tasks.scheduler import sync_schedule_triggers

    asyncio.run(sync_schedule_triggers())
    return {"status": "synced"}

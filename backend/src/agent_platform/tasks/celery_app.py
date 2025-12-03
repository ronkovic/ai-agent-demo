"""Celery application configuration."""

from celery import Celery

from agent_platform.core.config import settings

celery_app = Celery(
    "agent_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["agent_platform.tasks.workflow_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5分
    worker_prefetch_multiplier=1,
    # リトライ設定
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Celery Beat スケジュール（動的に更新される）
celery_app.conf.beat_schedule = {}

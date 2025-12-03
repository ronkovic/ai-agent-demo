"""Celery Beat scheduler synchronization."""

from datetime import UTC, datetime

from celery.schedules import crontab
from croniter import croniter
from sqlalchemy import select

from agent_platform.db import AsyncSessionLocal, ScheduleTrigger
from agent_platform.tasks.celery_app import celery_app


def parse_cron_to_celery(cron_expression: str) -> crontab:
    """cron式をCelery crontabに変換.

    Args:
        cron_expression: 標準的なcron式 (分 時 日 月 曜日)

    Returns:
        Celery crontab オブジェクト

    Raises:
        ValueError: 無効なcron式
    """
    parts = cron_expression.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_expression}")

    minute, hour, day_of_month, month_of_year, day_of_week = parts
    return crontab(
        minute=minute,
        hour=hour,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
        day_of_week=day_of_week,
    )


async def sync_schedule_triggers() -> None:
    """DBのスケジュールトリガーをCelery Beatに同期."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ScheduleTrigger).where(ScheduleTrigger.is_active == True)  # noqa: E712
        )
        triggers = result.scalars().all()

        new_schedule: dict = {}
        for trigger in triggers:
            task_name = f"schedule-trigger-{trigger.id}"
            try:
                new_schedule[task_name] = {
                    "task": "agent_platform.tasks.workflow_tasks.scheduled_workflow_trigger",
                    "schedule": parse_cron_to_celery(trigger.cron_expression),
                    "args": [str(trigger.id)],
                }

                # next_run_at 計算
                cron = croniter(trigger.cron_expression, datetime.now(UTC))
                trigger.next_run_at = cron.get_next(datetime)

            except ValueError:
                # 無効なcron式はスキップ
                continue

        await db.commit()

        # Celery Beat スケジュール更新
        celery_app.conf.beat_schedule = new_schedule


def get_next_run_time(cron_expression: str, base_time: datetime | None = None) -> datetime:
    """次回実行時刻を計算.

    Args:
        cron_expression: cron式
        base_time: 基準時刻 (デフォルト: 現在時刻)

    Returns:
        次回実行時刻
    """
    base = base_time or datetime.now(UTC)
    cron = croniter(cron_expression, base)
    return cron.get_next(datetime)


def validate_cron_expression(cron_expression: str) -> bool:
    """cron式のバリデーション.

    Args:
        cron_expression: cron式

    Returns:
        有効ならTrue
    """
    try:
        parts = cron_expression.split()
        if len(parts) != 5:
            return False
        croniter(cron_expression, datetime.now(UTC))
        return True
    except (ValueError, KeyError):
        return False

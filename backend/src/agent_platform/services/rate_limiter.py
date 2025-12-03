"""Rate Limiter service using Redis."""

from datetime import UTC, datetime
from uuid import UUID

import redis.asyncio as redis

from agent_platform.core.config import settings


class RateLimiter:
    """Redis Token Bucket Rate Limiter.

    Sliding Window カウンターアルゴリズムを使用。
    """

    def __init__(self) -> None:
        """Initialize Redis connection."""
        self._redis: redis.Redis | None = None

    async def _get_redis(self) -> redis.Redis:
        """Get Redis connection (lazy initialization)."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.celery_broker_url,
                decode_responses=True,
            )
        return self._redis

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int = 3600,
    ) -> tuple[bool, int]:
        """Rate limit check using sliding window.

        Args:
            key: Rate limit key (e.g., api_key_id)
            limit: Maximum requests per window
            window_seconds: Time window in seconds (default: 1 hour)

        Returns:
            Tuple of (allowed: bool, remaining: int)
        """
        r = await self._get_redis()
        now = int(datetime.now(UTC).timestamp())
        window_start = now - window_seconds

        pipe = r.pipeline()

        # 古いエントリを削除
        pipe.zremrangebyscore(key, 0, window_start)
        # 現在のカウント
        pipe.zcard(key)
        # 新しいエントリを追加
        pipe.zadd(key, {str(now): now})
        # TTL設定
        pipe.expire(key, window_seconds)

        results = await pipe.execute()
        current_count = results[1]

        if current_count >= limit:
            return False, 0

        return True, limit - current_count - 1

    async def get_remaining(
        self,
        key: str,
        limit: int,
        window_seconds: int = 3600,
    ) -> int:
        """Get remaining requests without incrementing.

        Args:
            key: Rate limit key
            limit: Maximum requests per window
            window_seconds: Time window in seconds

        Returns:
            Remaining request count
        """
        r = await self._get_redis()
        now = int(datetime.now(UTC).timestamp())
        window_start = now - window_seconds

        # 古いエントリを削除してカウント
        await r.zremrangebyscore(key, 0, window_start)
        current_count = await r.zcard(key)

        return max(0, limit - current_count)

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


# シングルトンインスタンス
rate_limiter = RateLimiter()


def get_rate_limit_key(api_key_id: UUID) -> str:
    """Generate rate limit key.

    Args:
        api_key_id: API key ID

    Returns:
        Rate limit key string
    """
    return f"rate_limit:{api_key_id}"

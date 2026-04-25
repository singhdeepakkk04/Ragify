"""
Redis-backed sliding window rate limiter.
Configurable per-endpoint: query/upload/mutation/default buckets.
"""

import ssl
import time
from datetime import datetime, timezone
import redis.asyncio as redis
from fastapi import HTTPException, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_authenticated_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.usage_log import UsageLog

# Redis connection — URL goes through Settings so password/host changes
# are picked up from .env (see config.py REDIS_URL)
_redis_ssl = None
if settings.REDIS_URL.startswith("rediss://") and settings.REDIS_VERIFY_SSL:
    _redis_ssl = ssl.create_default_context()
elif settings.REDIS_URL.startswith("rediss://"):
    _redis_ssl = ssl._create_unverified_context()

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    username=(settings.REDIS_USERNAME or None),
    password=(settings.REDIS_PASSWORD or None),
    ssl=_redis_ssl,
)

# Default rate limits per category
WINDOW_SECONDS = settings.RATE_LIMIT_WINDOW_SECONDS
RATE_LIMITS = {
    "query": settings.RATE_LIMIT_RAG_PER_MIN,
    "upload": settings.RATE_LIMIT_UPLOAD_PER_MIN,
    "mutation": settings.RATE_LIMIT_MUTATION_PER_MIN,
    "default": settings.RATE_LIMIT_DEFAULT_PER_MIN,
}


async def _enforce_rate_limit(
    user_id: int, category: str, limit: int, window: int
) -> None:
    """Core rate limit enforcement logic. Raises 429 if exceeded."""
    now = time.time()
    key = f"ratelimit:{category}:{user_id}"
    cutoff = now - window

    try:
        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, "-inf", cutoff)
            pipe.zcard(key)
            _, request_count = await pipe.execute()
    except Exception as exc:
        # Fail open — rate limiter unavailability should not block the request
        import logging
        logging.getLogger(__name__).warning(f"Rate limiter Redis error (failing open): {exc}")
        return

    if request_count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {limit} {category} requests per {window}s.",
            headers={"Retry-After": str(window)},
        )

    try:
        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, window)
            await pipe.execute()
    except Exception:
        pass  # Recording failure is non-critical


def _make_rate_limit_dependency(category: str, limit: int | None = None, window: int | None = None):
    bucket_limit = limit or RATE_LIMITS.get(category, RATE_LIMITS["default"])
    bucket_window = window or WINDOW_SECONDS

    async def _dep(current_user: User = Depends(get_authenticated_user)) -> User:
        await _enforce_rate_limit(current_user.id, category, bucket_limit, bucket_window)
        return current_user

    return _dep


# Common dependencies
check_rate_limit = _make_rate_limit_dependency("query")
check_upload_rate_limit = _make_rate_limit_dependency("upload")
check_mutation_rate_limit = _make_rate_limit_dependency("mutation")
check_default_rate_limit = _make_rate_limit_dependency("default")


async def enforce_daily_query_quota(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_rate_limit),
) -> User:
    """Daily tenant quota (per user). Disabled when TENANT_DAILY_QUERY_LIMIT <= 0."""
    limit = settings.TENANT_DAILY_QUERY_LIMIT
    if limit and limit > 0:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(func.count()).where(
                UsageLog.user_id == current_user.id,
                UsageLog.created_at >= today_start,
            )
        )
        used = result.scalar() or 0
        if used >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Daily quota exceeded. Max {limit} queries per day.",
                headers={"Retry-After": "86400"},
            )
    return current_user


async def get_remaining_requests(user_id: int) -> dict:
    """Get rate limit status for a user (query bucket)."""
    now = time.time()
    key = f"ratelimit:query:{user_id}"
    cutoff = now - WINDOW_SECONDS

    limit = RATE_LIMITS["query"]
    try:
        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, "-inf", cutoff)
            pipe.zcard(key)
            _, used = await pipe.execute()
    except Exception:
        used = 0

    return {
        "limit": limit,
        "remaining": max(0, limit - used),
        "used": used,
        "window_seconds": WINDOW_SECONDS,
    }

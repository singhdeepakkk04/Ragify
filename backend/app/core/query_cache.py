"""
Redis-backed query cache using local Docker Redis.
Scoped to (user_id, project_id, query) — no cross-user or cross-project leakage.

Falls back to in-memory cache if Redis is unavailable.
"""

import hashlib
import json
import logging
import time
from collections import OrderedDict
from typing import Optional, Dict, Any

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_TTL = 1800  # 30 minutes
MAX_INMEMORY_ENTRIES = 500  # fallback LRU size


class RedisQueryCache:
    """
    Docker Redis cache with in-memory fallback.
    Keys are scoped to user_id + project_id + normalized query.
    """

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._fallback: OrderedDict[str, Dict] = OrderedDict()
        self._stats = {"hits": 0, "misses": 0}
        self._using_redis = False
        self._connect()

    def _connect(self):
        """Try to connect to local Docker Redis. Fall back to in-memory if unavailable."""
        redis_url = getattr(settings, 'REDIS_URL', '') or 'redis://localhost:6379'
        if not redis_url:
            logger.warning("[Cache] No REDIS_URL set — using in-memory fallback")
            return

        try:
            self._redis = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            self._redis.ping()
            self._using_redis = True
            logger.info("[Cache] Connected to Docker Redis ✓")
        except Exception as e:
            logger.warning(f"[Cache] Redis connection failed: {e} — using in-memory fallback")
            self._redis = None

    @staticmethod
    def _make_key(user_id: int, project_id: int, query: str) -> str:
        """Cache key scoped to user + project + normalized query."""
        normalized = query.lower().strip()
        raw = f"{user_id}:{project_id}:{normalized}"
        return f"ragify:cache:{hashlib.sha256(raw.encode()).hexdigest()}"

    @staticmethod
    def _project_pattern(project_id: int) -> str:
        """Pattern for invalidating all keys of a project."""
        return f"ragify:proj:{project_id}:*"

    @staticmethod
    def _project_key(project_id: int, cache_key: str) -> str:
        """Secondary key mapping a project to its cache entries."""
        return f"ragify:proj:{project_id}:{cache_key}"

    # ── GET ──

    def get(self, user_id: int, project_id: int, query: str) -> Optional[Dict[str, Any]]:
        """Get cached result. Returns None on miss or expired entry."""
        key = self._make_key(user_id, project_id, query)

        if self._using_redis and self._redis:
            try:
                raw = self._redis.get(key)
                if raw:
                    self._stats["hits"] += 1
                    logger.info(f"[Cache] Redis HIT for {key[:30]}...")
                    return json.loads(raw)
                self._stats["misses"] += 1
                return None
            except Exception as e:
                logger.warning(f"[Cache] Redis GET error: {e}")

        # Fallback
        entry = self._fallback.get(key)
        if entry and time.time() - entry["ts"] < DEFAULT_TTL:
            self._fallback.move_to_end(key)
            self._stats["hits"] += 1
            logger.info(f"[Cache] Memory HIT for {key[:30]}...")
            return entry["data"]
        elif entry:
            del self._fallback[key]
        self._stats["misses"] += 1
        return None

    # ── SET ──

    def set_with_meta(self, user_id: int, project_id: int, query: str, data: Dict[str, Any]):
        """Store result with project association for invalidation."""
        key = self._make_key(user_id, project_id, query)
        serialized = json.dumps(data, default=str)

        if self._using_redis and self._redis:
            try:
                pipe = self._redis.pipeline()
                pipe.setex(key, DEFAULT_TTL, serialized)
                # Track which keys belong to this project (for invalidation)
                proj_key = self._project_key(project_id, key)
                pipe.setex(proj_key, DEFAULT_TTL, key)
                pipe.execute()
                logger.info(f"[Cache] Redis SET {key[:30]}...")
                return
            except Exception as e:
                logger.warning(f"[Cache] Redis SET error: {e}")

        # Fallback
        while len(self._fallback) >= MAX_INMEMORY_ENTRIES:
            self._fallback.popitem(last=False)
        self._fallback[key] = {"data": data, "ts": time.time()}
        logger.info(f"[Cache] Memory SET {key[:30]}...")

    # Alias for backward compatibility
    def set(self, user_id: int, project_id: int, query: str, data: Dict[str, Any]):
        self.set_with_meta(user_id, project_id, query, data)

    # ── INVALIDATE ──

    def invalidate_project(self, project_id: int):
        """Invalidate all cached entries for a project."""
        if self._using_redis and self._redis:
            try:
                pattern = self._project_pattern(project_id)
                keys = list(self._redis.scan_iter(match=pattern, count=100))
                if keys:
                    # Get the actual cache keys stored as values
                    cache_keys = [v for v in self._redis.mget(keys) if v]
                    # Delete both the project mapping keys and cache keys
                    all_keys = keys + cache_keys
                    if all_keys:
                        self._redis.delete(*all_keys)
                    logger.info(f"[Cache] Redis invalidated {len(cache_keys)} entries for project {project_id}")
                return
            except Exception as e:
                logger.warning(f"[Cache] Redis invalidation error: {e}")

        # Fallback — scan all entries (less efficient but works)
        to_delete = [k for k, v in self._fallback.items() if v.get("project_id") == project_id]
        for k in to_delete:
            del self._fallback[k]
        if to_delete:
            logger.info(f"[Cache] Memory invalidated {len(to_delete)} entries for project {project_id}")

    # ── STATS ──

    @property
    def stats(self) -> Dict[str, Any]:
        total = self._stats["hits"] + self._stats["misses"]
        info = {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": round(self._stats["hits"] / total * 100, 1) if total > 0 else 0,
            "backend": "redis" if self._using_redis else "in-memory",
        }

        if self._using_redis and self._redis:
            try:
                db_size = self._redis.dbsize()
                info["redis_keys"] = db_size
            except Exception:
                pass
        else:
            info["entries"] = len(self._fallback)

        return info


# Global singleton
query_cache = RedisQueryCache()

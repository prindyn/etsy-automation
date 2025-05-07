import redis.asyncio as redis
from app.core.config import settings
import json
import hashlib

_redis = redis.from_url(settings.REDIS_URL, decode_responses=True)


def _make_cache_key(prefix: str, limit: int) -> str:
    return f"{prefix}:{hashlib.sha256(str(limit).encode()).hexdigest()}"


async def get_cached_keywords(limit: int) -> list | None:
    key = _make_cache_key("top_keywords", limit)
    cached = await _redis.get(key)
    if cached:
        return json.loads(cached)
    return None


async def set_cached_keywords(limit: int, data: list, ttl_sec: int = 3600):
    key = _make_cache_key("top_keywords", limit)
    await _redis.set(key, json.dumps(data), ex=ttl_sec)

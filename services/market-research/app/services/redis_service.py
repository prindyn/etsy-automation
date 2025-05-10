import json
from typing import Optional, Protocol, Union
from redis.asyncio import Redis
from app.core.config import settings

# === Redis Singleton ===
redis = Redis.from_url(settings.REDIS_URL)


# === Unified Redis Interface ===
class RedisCapable(Protocol):
    def cache_key(self) -> str: ...
    def get_value(self) -> Union[dict, list, str]: ...


# === Set Cache / Queue ===
async def set_cache(
    storage: RedisCapable,
    ttl_sec: Optional[int] = None,
):
    value = storage.get_value()
    raw = value if isinstance(value, str) else json.dumps(value)
    await redis.set(storage.cache_key(), raw, ex=ttl_sec)


# === Get Cache / Queue ===
async def get_cache(
    storage: RedisCapable,
    parse_json: bool = True,
) -> Optional[Union[dict, list, str]]:
    raw = await redis.get(storage.cache_key())
    if raw is None:
        return None
    return json.loads(raw) if parse_json else raw


# === Delete Cache / Queue Key ===
async def delete_cache(storage: RedisCapable) -> bool:
    return await redis.delete(storage.cache_key()) == 1

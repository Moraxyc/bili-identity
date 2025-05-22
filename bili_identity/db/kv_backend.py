import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

import redis.asyncio as redis

from bili_identity.config import get_config

logger = logging.getLogger(__name__)


class KVBackend(ABC):
    @abstractmethod
    async def set(
        self, key: str, value: str, ttl: Optional[int] = None
    ) -> None:
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    async def aclose(self) -> None:  # 仅redis
        pass


class RedisBackend(KVBackend):
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        if ttl:
            await self.redis.setex(key, ttl, value)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def aclose(self) -> None:
        await self.redis.aclose()


class MemoryBackend(KVBackend):
    def __init__(self):
        self.store = {}
        self.lock = asyncio.Lock()

    async def set(
        self, key: str, value: str, ttl: Optional[int] = None
    ) -> None:
        async with self.lock:
            expire_at = time.time() + ttl if ttl else None
            self.store[key] = (value, expire_at)
            logger.debug(
                f"[MemoryBackend] SET {key} -> {value} (ttl={ttl})"
            )

    async def get(self, key: str) -> Optional[str]:
        async with self.lock:
            item = self.store.get(key)
            if not item:
                return None
            value, expire_at = item
            if expire_at and time.time() > expire_at:
                del self.store[key]
                logger.debug(f"[MemoryBackend] EXPIRED {key}")
                return None
            logger.debug(f"[MemoryBackend] GET {key} -> {value}")
            return value

    async def delete(self, key: str) -> None:
        async with self.lock:
            removed = self.store.pop(key, None)
            logger.debug(
                f"[MemoryBackend] DELETE {key}, existed: {removed is not None}"
            )

    async def aclose(self) -> None:
        # 内存的不需要关
        pass


_kv_session: Optional[KVBackend] = None


async def init_kv():
    global _kv_session
    config = get_config()

    if config.redis.enable:
        redis_client = redis.from_url(
            config.redis.uri, decode_responses=True
        )
        await redis_client.ping()
        _kv_session = RedisBackend(redis_client)
        logger.debug("Redis 作为 KV 存储后端已启用")
    else:
        _kv_session = MemoryBackend()
        logger.debug("使用内存作为 KV 存储后端")


def get_kv_session() -> KVBackend:
    if _kv_session is None:
        raise RuntimeError(
            "kv_session 尚未初始化，请确认 init_kv() 已在应用启动时执行"
        )
    return _kv_session

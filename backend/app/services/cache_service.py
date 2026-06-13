"""
Cache Service using Redis for performance optimization
"""

import json
from typing import Optional, Any
from datetime import datetime, timedelta, timezone
from functools import wraps
import hashlib

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Try to import async Redis
try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore
    logger.warning("Redis not available - caching disabled")


# === HELPERS para manejo de errores Redis (elimina duplicación) ===
def handle_redis_error(operation: str, error: Exception) -> None:
    if redis and isinstance(error, redis.RedisError):
        logger.error(f"Redis {operation} error: {error}")


def safe_redis_operation(operation_name: str):
    """
    Decorator para envolver operaciones Redis con manejo de errores.
    Uso: @safe_redis_operation('get') def get(self, key): ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_redis_error(operation_name, e)
                return None

        return wrapper

    return decorator


class CacheService:
    """
    Redis-based cache service with fallback to in-memory for development.
    Supports automatic serialization and TTL.
    """

    def __init__(self):
        self.redis_client = None
        self.in_memory_cache = {}  # Fallback for development
        self.enabled = False

        if REDIS_AVAILABLE and settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8")
                self.enabled = True
                logger.info("Cache service (Redis) connected")
            except redis.RedisError as e:
                logger.error(f"Failed to connect to Redis cache: {e}")
                logger.info("Using in-memory cache as fallback")
            except (OSError, ConnectionError, TimeoutError) as e:
                logger.critical(f"Unexpected error connecting to Redis: {e}")
                logger.info("Using in-memory cache as fallback")

    def _encode(self, value: Any) -> bytes:
        """Serialize value to bytes using only JSON (secure, no pickle)"""
        return json.dumps(value, default=str).encode("utf-8")

    def _decode(self, data: bytes) -> Any:
        """Deserialize bytes to value using only JSON (secure, no pickle)"""
        return json.loads(data.decode("utf-8"))

    def _make_key(self, key: str) -> str:
        """Add namespace to key"""
        return f"costarica:cache:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        full_key = self._make_key(key)

        if self.redis_client:
            try:
                data = await self.redis_client.get(full_key)
                if data:
                    return self._decode(data)
            except Exception as e:
                handle_redis_error("get", e)

        # Fallback to in-memory
        if full_key in self.in_memory_cache:
            value, expires = self.in_memory_cache[full_key]
            if datetime.now(timezone.utc) < expires:
                return value
            else:
                del self.in_memory_cache[full_key]

        return None

    async def set(
        self, key: str, value: Any, ttl: int = 3600, tags: Optional[list] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default 1 hour)
            tags: Optional tags for group invalidation

        Returns:
            True if successfully cached
        """
        full_key = self._make_key(key)

        # Store tags for later invalidation
        if tags:
            for tag in tags:
                tag_key = self._make_key(f"tag:{tag}")
                if self.redis_client:
                    try:
                        await self.redis_client.sadd(tag_key, full_key)
                        await self.redis_client.expire(tag_key, ttl * 2)
                    except Exception as e:
                        handle_redis_error("tag", e)

        if self.redis_client:
            try:
                data = self._encode(value)
                await self.redis_client.setex(full_key, ttl, data)
                return True
            except Exception as e:
                handle_redis_error("set", e)

        # Fallback to in-memory
        expires = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        self.in_memory_cache[full_key] = (value, expires)
        return True

    async def delete(self, key: str) -> bool:
        """Delete a specific key from cache"""
        full_key = self._make_key(key)

        if self.redis_client:
            try:
                result = await self.redis_client.delete(full_key)
                return result > 0
            except Exception as e:
                handle_redis_error("delete", e)

        if full_key in self.in_memory_cache:
            del self.in_memory_cache[full_key]
            return True

        return False

    async def invalidate_tag(self, tag: str) -> int:
        """
        Invalidate all keys with a specific tag.

        Args:
            tag: Tag to invalidate

        Returns:
            Number of keys invalidated
        """
        tag_key = self._make_key(f"tag:{tag}")
        count = 0

        if self.redis_client:
            try:
                keys = await self.redis_client.smembers(tag_key)
                if keys:
                    count = await self.redis_client.delete(*keys)
                await self.redis_client.delete(tag_key)
                return count
            except Exception as e:
                handle_redis_error("invalidate_tag", e)

        # Fallback: clear all cache with tag prefix (simplified)
        keys_to_delete = [k for k in self.in_memory_cache.keys() if tag in k]
        for k in keys_to_delete:
            del self.in_memory_cache[k]
            count += 1

        return count

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate keys matching a pattern.

        Args:
            pattern: Pattern to match (e.g., "properties:*")

        Returns:
            Number of keys invalidated
        """
        full_pattern = self._make_key(pattern)
        count = 0

        if self.redis_client:
            try:
                keys = await self.redis_client.keys(full_pattern)
                if keys:
                    count = await self.redis_client.delete(*keys)
                return count
            except Exception as e:
                handle_redis_error("invalidate_pattern", e)

        # Fallback
        keys_to_delete = [
            k for k in self.in_memory_cache.keys() if full_pattern.replace("*", "") in k
        ]
        for k in keys_to_delete:
            del self.in_memory_cache[k]
            count += 1

        return count

    async def clear(self) -> bool:
        """Clear all cache"""
        if self.redis_client:
            try:
                pattern = self._make_key("*")
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                return True
            except Exception as e:
                handle_redis_error("clear", e)

        self.in_memory_cache.clear()
        return True

    def cached(self, key_prefix: str, ttl: int = 3600, tags: Optional[list] = None):
        """
        Decorator to cache function results.

        Args:
            key_prefix: Prefix for cache key
            ttl: Cache TTL in seconds
            tags: Tags for group invalidation
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key_parts = [key_prefix]

                # Add args (skip self/cls)
                for arg in args[1:] if args else []:
                    key_parts.append(str(arg))

                # Add kwargs (sorted for consistency)
                for k in sorted(kwargs.keys()):
                    key_parts.append(f"{k}={kwargs[k]}")

                cache_key = hashlib.md5(
                    ":".join(key_parts).encode(), usedforsecurity=False
                ).hexdigest()

                # Try to get from cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                await self.set(cache_key, result, ttl=ttl, tags=tags)
                logger.debug(f"Cache set: {cache_key}")

                return result

            return wrapper

        return decorator


# Global cache service instance
cache = CacheService()

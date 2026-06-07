"""
Redis Cache Module
Provides caching functionality for API endpoints
"""
import json
from typing import Optional, Any
from functools import wraps
import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get or create Redis client singleton"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL or "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client


async def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        r = await get_redis()
        value = await r.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning(f"Cache get error for key {key}: {e}")
        return None


async def set_cache(
    key: str,
    value: Any,
    ttl: int = 3600
) -> bool:
    """Set value in cache with TTL (default 1 hour)"""
    try:
        r = await get_redis()
        await r.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.warning(f"Cache set error for key {key}: {e}")
        return False


async def delete_cache(key: str) -> bool:
    """Delete key from cache"""
    try:
        r = await get_redis()
        await r.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache delete error for key {key}: {e}")
        return False


async def delete_pattern(pattern: str) -> int:
    """Delete all keys matching pattern"""
    try:
        r = await get_redis()
        keys = []
        async for key in r.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            return await r.delete(*keys)
        return 0
    except Exception as e:
        logger.warning(f"Cache pattern delete error for {pattern}: {e}")
        return 0


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    parts = [str(arg) for arg in args]
    for k, v in sorted(kwargs.items()):
        parts.append(f"{k}={v}")
    return ":".join(parts)


def cached(ttl: int = 3600, key_prefix: str = "api"):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=3600, key_prefix="properties")
        async def get_properties():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(a) for a in args if a)
            for k, v in sorted(kwargs.items()):
                if v is not None:
                    key_parts.append(f"{k}={v}")
            cache_key_str = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = await get_cache(cache_key_str)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key_str}")
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await set_cache(cache_key_str, result, ttl)
            logger.debug(f"Cache miss: {cache_key_str}")
            
            return result
        return wrapper
    return decorator


async def cache_invalidate(prefix: str):
    """Invalidate all cache entries with given prefix"""
    await delete_pattern(f"{prefix}:*")
    logger.info(f"Cache invalidated for prefix: {prefix}")
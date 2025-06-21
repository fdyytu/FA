"""Discord Caching Service - Core caching functionality"""
import redis
import json
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DiscordCache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection untuk Discord caching"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis unavailable, using memory cache: {e}")
            self.redis_client = None
            self._memory_cache = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached data by key"""
        try:
            if self.redis_client:
                data = self.redis_client.get(f"discord:{key}")
                return json.loads(data) if data else None
            else:
                cached = self._memory_cache.get(key)
                if cached and cached['expires'] > datetime.now():
                    return cached['data']
                elif cached:
                    del self._memory_cache[key]
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set cached data dengan TTL (default 5 menit)"""
        try:
            if self.redis_client:
                return self.redis_client.setex(f"discord:{key}", ttl, json.dumps(value, default=str))
            else:
                self._memory_cache[key] = {'data': value, 'expires': datetime.now() + timedelta(seconds=ttl)}
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
# Global cache instance
discord_cache = DiscordCache()

"""
Redis Cache Service Implementation
Implementasi konkret dari ICacheService menggunakan Redis
"""

import json
import redis.asyncio as redis
from typing import Any, Optional, Union, Dict
from datetime import timedelta
import logging
from app.cache.interfaces.cache_interfaces import ICacheService, ICacheSerializer
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class JSONCacheSerializer(ICacheSerializer):
    """JSON serializer untuk cache data"""
    
    def serialize(self, data: Any) -> str:
        """Serialize data ke JSON string"""
        try:
            return json.dumps(data, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error serializing cache data: {e}")
            raise
    
    def deserialize(self, data: str) -> Any:
        """Deserialize JSON string ke data"""
        try:
            return json.loads(data)
        except Exception as e:
            logger.error(f"Error deserializing cache data: {e}")
            raise


class RedisCacheService(ICacheService):
    """
    Redis implementation dari ICacheService
    Mengikuti Single Responsibility Principle - hanya menangani Redis operations
    """
    
    def __init__(
        self, 
        redis_url: str = None,
        password: str = None,
        db: int = 0,
        serializer: ICacheSerializer = None
    ):
        self.redis_url = redis_url or settings.REDIS_URL
        self.password = password or settings.REDIS_PASSWORD
        self.db = db or int(settings.REDIS_DB)
        self.serializer = serializer or JSONCacheSerializer()
        self._redis_client = None
    
    async def _get_redis_client(self) -> redis.Redis:
        """Lazy initialization Redis client"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    self.redis_url,
                    password=self.password,
                    db=self.db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                await self._redis_client.ping()
                logger.info("Redis connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        
        return self._redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Ambil data dari Redis cache"""
        try:
            client = await self._get_redis_client()
            cached_data = await client.get(key)
            
            if cached_data is None:
                return None
            
            return self.serializer.deserialize(cached_data)
            
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Simpan data ke Redis cache"""
        try:
            client = await self._get_redis_client()
            serialized_data = self.serializer.serialize(value)
            
            # Convert timedelta to seconds if needed
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            result = await client.set(key, serialized_data, ex=ttl)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Hapus data dari Redis cache"""
        try:
            client = await self._get_redis_client()
            result = await client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Cek apakah key ada di Redis cache"""
        try:
            client = await self._get_redis_client()
            result = await client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Hapus data dari Redis berdasarkan pattern"""
        try:
            client = await self._get_redis_client()
            
            if pattern:
                # Hapus berdasarkan pattern
                keys = await client.keys(pattern)
                if keys:
                    result = await client.delete(*keys)
                    return result > 0
                return True
            else:
                # Hapus semua data di database
                result = await client.flushdb()
                return bool(result)
                
        except Exception as e:
            logger.error(f"Error clearing cache with pattern {pattern}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Cek kesehatan Redis connection"""
        try:
            client = await self._get_redis_client()
            await client.ping()
            info = await client.info()
            
            return {
                "status": "healthy",
                "type": "redis",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "uptime": info.get("uptime_in_seconds", 0)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "type": "redis",
                "error": str(e)
            }
    
    async def close(self):
        """Tutup Redis connection"""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
            logger.info("Redis connection closed")

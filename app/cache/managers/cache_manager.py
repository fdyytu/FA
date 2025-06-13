"""
Cache Manager Implementation
Mengelola multiple cache instances dengan fallback mechanism
"""

import logging
from typing import Dict, Any, Optional
from app.cache.interfaces.cache_interfaces import ICacheService, ICacheManager, ICacheKeyGenerator
from app.cache.implementations.redis_cache import RedisCacheService
from app.cache.implementations.memory_cache import MemoryCacheService
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class CacheKeyGenerator(ICacheKeyGenerator):
    """
    Generator untuk cache keys yang konsisten
    Mengikuti DRY principle - satu tempat untuk generate keys
    """
    
    def __init__(self, app_prefix: str = "ppob_api"):
        self.app_prefix = app_prefix
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key dengan format: app_prefix:prefix:args:kwargs"""
        key_parts = [self.app_prefix, prefix]
        
        # Tambahkan args
        if args:
            key_parts.extend([str(arg) for arg in args])
        
        # Tambahkan kwargs (sorted untuk konsistensi)
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                key_parts.append(f"{k}:{v}")
        
        return ":".join(key_parts)
    
    def generate_pattern(self, prefix: str, pattern: str = "*") -> str:
        """Generate pattern untuk cache key matching"""
        return f"{self.app_prefix}:{prefix}:{pattern}"


class CacheManager(ICacheManager):
    """
    Cache Manager dengan fallback mechanism
    Mengikuti Open/Closed Principle - mudah extend dengan cache type baru
    """
    
    def __init__(self):
        self._cache_services: Dict[str, ICacheService] = {}
        self._primary_cache_type = "redis"
        self._fallback_cache_type = "memory"
        self._key_generator = CacheKeyGenerator()
        self._initialized = False
    
    async def initialize(self):
        """Initialize cache services"""
        if self._initialized:
            return
        
        try:
            # Initialize Redis cache
            redis_cache = RedisCacheService(
                redis_url=settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=int(settings.REDIS_DB)
            )
            self._cache_services["redis"] = redis_cache
            logger.info("Redis cache service initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
        
        # Initialize Memory cache sebagai fallback
        memory_cache = MemoryCacheService(max_size=1000)
        self._cache_services["memory"] = memory_cache
        logger.info("Memory cache service initialized")
        
        self._initialized = True
    
    async def get_cache_service(self, cache_type: str = "default") -> ICacheService:
        """
        Ambil cache service dengan fallback mechanism
        Jika primary cache gagal, gunakan fallback
        """
        if not self._initialized:
            await self.initialize()
        
        if cache_type == "default":
            # Coba primary cache dulu
            primary_cache = self._cache_services.get(self._primary_cache_type)
            if primary_cache:
                # Test health primary cache
                health = await primary_cache.health_check()
                if health.get("status") == "healthy":
                    return primary_cache
                else:
                    logger.warning(f"Primary cache ({self._primary_cache_type}) unhealthy, using fallback")
            
            # Gunakan fallback cache
            fallback_cache = self._cache_services.get(self._fallback_cache_type)
            if fallback_cache:
                return fallback_cache
            
            raise Exception("No healthy cache service available")
        
        # Return specific cache type
        cache_service = self._cache_services.get(cache_type)
        if not cache_service:
            raise Exception(f"Cache service type '{cache_type}' not found")
        
        return cache_service
    
    async def health_check(self) -> Dict[str, Any]:
        """Cek kesehatan semua cache services"""
        if not self._initialized:
            await self.initialize()
        
        health_results = {}
        overall_status = "healthy"
        
        for cache_type, cache_service in self._cache_services.items():
            try:
                health = await cache_service.health_check()
                health_results[cache_type] = health
                
                if health.get("status") != "healthy":
                    if cache_type == self._primary_cache_type:
                        overall_status = "degraded"  # Primary unhealthy tapi ada fallback
                    
            except Exception as e:
                health_results[cache_type] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                if cache_type == self._primary_cache_type:
                    overall_status = "degraded"
        
        # Jika semua cache unhealthy
        if all(h.get("status") != "healthy" for h in health_results.values()):
            overall_status = "unhealthy"
        
        return {
            "overall_status": overall_status,
            "services": health_results,
            "primary_cache": self._primary_cache_type,
            "fallback_cache": self._fallback_cache_type
        }
    
    def get_key_generator(self) -> ICacheKeyGenerator:
        """Ambil key generator instance"""
        return self._key_generator
    
    async def clear_all_caches(self, pattern: Optional[str] = None):
        """Clear semua cache services"""
        if not self._initialized:
            await self.initialize()
        
        results = {}
        for cache_type, cache_service in self._cache_services.items():
            try:
                result = await cache_service.clear(pattern)
                results[cache_type] = {"success": result}
            except Exception as e:
                results[cache_type] = {"success": False, "error": str(e)}
                logger.error(f"Failed to clear {cache_type} cache: {e}")
        
        return results
    
    async def close_all(self):
        """Tutup semua cache connections"""
        for cache_type, cache_service in self._cache_services.items():
            try:
                if hasattr(cache_service, 'close'):
                    await cache_service.close()
                logger.info(f"Closed {cache_type} cache service")
            except Exception as e:
                logger.error(f"Error closing {cache_type} cache: {e}")
        
        self._cache_services.clear()
        self._initialized = False


# Global cache manager instance
cache_manager = CacheManager()

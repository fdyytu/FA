"""
Cache Helper Class
Helper class untuk cache operations yang tidak menggunakan decorator
"""

import inspect
import logging
from typing import Any, Callable, Optional, Union
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheHelper:
    """
    Helper class untuk cache operations yang tidak menggunakan decorator
    Mengikuti KISS principle - simple interface untuk cache operations
    """
    
    @staticmethod
    async def get_or_set(
        key: str,
        factory_func: Callable,
        ttl: Optional[Union[int, timedelta]] = None,
        cache_type: str = "default"
    ) -> Any:
        """Get dari cache, jika tidak ada execute factory_func dan cache hasilnya"""
        try:
            from app.cache.managers.cache_manager import cache_manager
            
            cache_service = await cache_manager.get_cache_service(cache_type)
            
            cached_result = await cache_service.get(key)
            if cached_result is not None:
                return cached_result
            
            if inspect.iscoroutinefunction(factory_func):
                result = await factory_func()
            else:
                result = factory_func()
            
            await cache_service.set(key, result, ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Cache helper error for key {key}: {e}")
            if inspect.iscoroutinefunction(factory_func):
                return await factory_func()
            else:
                return factory_func()
    
    @staticmethod
    async def invalidate_pattern(
        pattern: str,
        cache_type: str = "default"
    ) -> bool:
        """Invalidate cache berdasarkan pattern"""
        try:
            from app.cache.managers.cache_manager import cache_manager
            
            cache_service = await cache_manager.get_cache_service(cache_type)
            return await cache_service.clear(pattern)
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")
            return False

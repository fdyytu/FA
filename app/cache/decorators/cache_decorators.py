"""
Cache Decorators
Decorator untuk caching yang dapat digunakan kembali (DRY Principle)
"""

import functools
import inspect
import logging
from typing import Any, Optional, Union, Callable, Dict
from datetime import timedelta
from app.cache.managers.cache_manager import cache_manager

logger = logging.getLogger(__name__)


def cache_result(
    ttl: Optional[Union[int, timedelta]] = None,
    key_prefix: str = None,
    cache_type: str = "default",
    skip_cache_on_error: bool = True
):
    """
    Decorator untuk cache hasil function
    
    Args:
        ttl: Time to live untuk cache
        key_prefix: Prefix untuk cache key
        cache_type: Tipe cache yang digunakan
        skip_cache_on_error: Skip cache jika ada error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Generate cache key
                cache_service = await cache_manager.get_cache_service(cache_type)
                key_generator = cache_manager.get_key_generator()
                
                # Gunakan function name sebagai prefix jika tidak ada key_prefix
                prefix = key_prefix or f"func:{func.__name__}"
                cache_key = key_generator.generate_key(prefix, *args, **kwargs)
                
                # Coba ambil dari cache
                cached_result = await cache_service.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                # Jika tidak ada di cache, execute function
                logger.debug(f"Cache miss for key: {cache_key}")
                result = await func(*args, **kwargs)
                
                # Simpan hasil ke cache
                await cache_service.set(cache_key, result, ttl)
                logger.debug(f"Cached result for key: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Cache error in {func.__name__}: {e}")
                if skip_cache_on_error:
                    # Jika ada error cache, tetap execute function
                    return await func(*args, **kwargs)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Untuk function synchronous, convert ke async
            import asyncio
            
            async def async_func(*args, **kwargs):
                return func(*args, **kwargs)
            
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        # Return wrapper yang sesuai berdasarkan function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cache_invalidate(
    key_patterns: Union[str, list],
    cache_type: str = "default"
):
    """
    Decorator untuk invalidate cache setelah function execution
    
    Args:
        key_patterns: Pattern atau list pattern untuk invalidate
        cache_type: Tipe cache yang digunakan
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Execute function dulu
                result = await func(*args, **kwargs)
                
                # Invalidate cache
                cache_service = await cache_manager.get_cache_service(cache_type)
                key_generator = cache_manager.get_key_generator()
                
                patterns = key_patterns if isinstance(key_patterns, list) else [key_patterns]
                
                for pattern in patterns:
                    # Generate pattern dengan args/kwargs jika diperlukan
                    if "{" in pattern:
                        # Format pattern dengan args/kwargs
                        formatted_pattern = pattern.format(*args, **kwargs)
                    else:
                        formatted_pattern = key_generator.generate_pattern(pattern)
                    
                    await cache_service.clear(formatted_pattern)
                    logger.debug(f"Invalidated cache pattern: {formatted_pattern}")
                
                return result
                
            except Exception as e:
                logger.error(f"Cache invalidation error in {func.__name__}: {e}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            import asyncio
            
            async def async_func(*args, **kwargs):
                return func(*args, **kwargs)
            
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cache_key_from_args(
    key_template: str,
    ttl: Optional[Union[int, timedelta]] = None,
    cache_type: str = "default"
):
    """
    Decorator untuk cache dengan custom key template
    
    Args:
        key_template: Template untuk generate key, contoh: "user:{user_id}:profile"
        ttl: Time to live untuk cache
        cache_type: Tipe cache yang digunakan
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                cache_service = await cache_manager.get_cache_service(cache_type)
                
                # Generate key dari template
                # Ambil parameter names dari function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Format key template dengan arguments
                cache_key = key_template.format(**bound_args.arguments)
                
                # Coba ambil dari cache
                cached_result = await cache_service.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Simpan ke cache
                await cache_service.set(cache_key, result, ttl)
                logger.debug(f"Cached result for key: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Cache error in {func.__name__}: {e}")
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            import asyncio
            
            async def async_func(*args, **kwargs):
                return func(*args, **kwargs)
            
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


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
        """
        Get dari cache, jika tidak ada execute factory_func dan cache hasilnya
        """
        try:
            cache_service = await cache_manager.get_cache_service(cache_type)
            
            # Coba ambil dari cache
            cached_result = await cache_service.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute factory function
            if inspect.iscoroutinefunction(factory_func):
                result = await factory_func()
            else:
                result = factory_func()
            
            # Cache hasil
            await cache_service.set(key, result, ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Cache helper error for key {key}: {e}")
            # Fallback ke factory function
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
            cache_service = await cache_manager.get_cache_service(cache_type)
            return await cache_service.clear(pattern)
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")
            return False

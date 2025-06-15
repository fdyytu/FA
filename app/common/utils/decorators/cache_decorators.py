"""
Cache Decorators - Unified Implementation
Decorator untuk caching yang dapat digunakan kembali (DRY Principle)
Menggabungkan implementasi dari cache/decorators dan common/utils/decorators
"""

import functools
import inspect
import logging
from typing import Any, Optional, Union, Callable, Dict
from datetime import timedelta

logger = logging.getLogger(__name__)


def cache_result(
    ttl: Optional[Union[int, timedelta]] = None,
    key_prefix: str = None,
    cache_type: str = "default",
    skip_cache_on_error: bool = True,
    key_template: str = None,  # Backward compatibility
    expire_seconds: int = 300  # Backward compatibility
):
    """
    Unified decorator untuk cache hasil function
    Mendukung kedua interface untuk backward compatibility
    
    Args:
        ttl: Time to live untuk cache (new interface)
        key_prefix: Prefix untuk cache key (new interface)
        cache_type: Tipe cache yang digunakan
        skip_cache_on_error: Skip cache jika ada error
        key_template: Template untuk cache key (legacy interface)
        expire_seconds: Cache expiration time (legacy interface)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Determine which cache implementation to use
                use_legacy = key_template is not None
                
                if use_legacy:
                    # Legacy implementation
                    try:
                        key_data = {
                            'args': args,
                            'kwargs': kwargs,
                            'func_name': func.__name__
                        }
                        cache_key = key_template.format(**key_data, **kwargs)
                    except (KeyError, ValueError):
                        cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                    
                    try:
                        from app.core.container import get_service
                        from app.core.interfaces import ICacheService
                        
                        cache_service = get_service(ICacheService)
                        cached_result = await cache_service.get(cache_key)
                        
                        if cached_result is not None:
                            logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                            return cached_result
                            
                    except Exception as e:
                        logger.warning(f"Cache get failed for {func.__name__}: {e}")
                    
                    result = await func(*args, **kwargs)
                    
                    try:
                        await cache_service.set(cache_key, result, expire_seconds)
                        logger.debug(f"Cached result for {func.__name__}: {cache_key}")
                    except Exception as e:
                        logger.warning(f"Cache set failed for {func.__name__}: {e}")
                    
                    return result
                
                else:
                    # New implementation
                    from app.cache.managers.cache_manager import cache_manager
                    
                    cache_service = await cache_manager.get_cache_service(cache_type)
                    key_generator = cache_manager.get_key_generator()
                    
                    prefix = key_prefix or f"func:{func.__name__}"
                    cache_key = key_generator.generate_key(prefix, *args, **kwargs)
                    
                    cached_result = await cache_service.get(cache_key)
                    if cached_result is not None:
                        logger.debug(f"Cache hit for key: {cache_key}")
                        return cached_result
                    
                    logger.debug(f"Cache miss for key: {cache_key}")
                    result = await func(*args, **kwargs)
                    
                    await cache_service.set(cache_key, result, ttl)
                    logger.debug(f"Cached result for key: {cache_key}")
                    
                    return result
                    
            except Exception as e:
                logger.error(f"Cache error in {func.__name__}: {e}")
                if skip_cache_on_error:
                    return await func(*args, **kwargs)
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


def cache_invalidate(
    key_patterns: Union[str, list],
    cache_type: str = "default",
    key_pattern: str = None  # Backward compatibility
):
    """
    Unified decorator untuk invalidate cache setelah function execution
    
    Args:
        key_patterns: Pattern atau list pattern untuk invalidate (new interface)
        cache_type: Tipe cache yang digunakan
        key_pattern: Pattern untuk cache keys (legacy interface)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                # Determine which implementation to use
                use_legacy = key_pattern is not None
                
                if use_legacy:
                    # Legacy implementation
                    try:
                        from app.core.container import get_service
                        from app.core.interfaces import ICacheService
                        
                        cache_service = get_service(ICacheService)
                        
                        try:
                            key_data = {
                                'args': args,
                                'kwargs': kwargs,
                                'func_name': func.__name__
                            }
                            invalidation_key = key_pattern.format(**key_data, **kwargs)
                        except (KeyError, ValueError):
                            invalidation_key = key_pattern
                        
                        await cache_service.delete_pattern(invalidation_key)
                        logger.debug(f"Cache invalidated for pattern: {invalidation_key}")
                        
                    except Exception as e:
                        logger.warning(f"Cache invalidation failed for {func.__name__}: {e}")
                
                else:
                    # New implementation
                    from app.cache.managers.cache_manager import cache_manager
                    
                    cache_service = await cache_manager.get_cache_service(cache_type)
                    key_generator = cache_manager.get_key_generator()
                    
                    patterns = key_patterns if isinstance(key_patterns, list) else [key_patterns]
                    
                    for pattern in patterns:
                        if "{" in pattern:
                            formatted_pattern = pattern.format(*args, **kwargs)
                        else:
                            formatted_pattern = key_generator.generate_pattern(pattern)
                        
                        await cache_service.clear(formatted_pattern)
                        logger.debug(f"Invalidated cache pattern: {formatted_pattern}")
                
                return result
                
            except Exception as e:
                logger.error(f"Cache invalidation error in {func.__name__}: {e}")
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
                from app.cache.managers.cache_manager import cache_manager
                
                cache_service = await cache_manager.get_cache_service(cache_type)
                
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                cache_key = key_template.format(**bound_args.arguments)
                
                cached_result = await cache_service.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                result = await func(*args, **kwargs)
                
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


def memoize(maxsize: int = 128):
    """
    Simple memoization decorator untuk function results
    
    Args:
        maxsize: Maximum cache size
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_order = []
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            
            if key in cache:
                cache_order.remove(key)
                cache_order.append(key)
                return cache[key]
            
            result = func(*args, **kwargs)
            
            cache[key] = result
            cache_order.append(key)
            
            if len(cache) > maxsize:
                oldest_key = cache_order.pop(0)
                del cache[oldest_key]
            
            return result
        
        wrapper.cache_clear = lambda: cache.clear() or cache_order.clear()
        wrapper.cache_info = lambda: {
            'hits': len([k for k in cache_order if k in cache]),
            'misses': len(cache_order) - len([k for k in cache_order if k in cache]),
            'maxsize': maxsize,
            'currsize': len(cache)
        }
        
        return wrapper
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

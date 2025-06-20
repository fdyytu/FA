"""
Cache Result Decorator
Decorator untuk caching hasil function dengan dukungan legacy dan new interface
"""

import functools
import inspect
import logging
from typing import Any, Optional, Union, Callable
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

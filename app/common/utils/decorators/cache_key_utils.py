"""
Cache Key Utilities
Utility functions untuk generate cache keys dari function arguments
"""

import functools
import inspect
import logging
from typing import Any, Callable, Optional, Union
from datetime import timedelta

logger = logging.getLogger(__name__)


def cache_key_from_args(
    key_template: str,
    ttl: Optional[Union[int, timedelta]] = None,
    cache_type: str = "default"
):
    """
    Decorator untuk generate cache key dari function arguments menggunakan template
    
    Args:
        key_template: Template string untuk cache key (e.g., "user:{user_id}:profile")
        ttl: Time to live untuk cache
        cache_type: Tipe cache yang digunakan
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                from app.cache.managers.cache_manager import cache_manager
                
                cache_service = await cache_manager.get_cache_service(cache_type)
                
                # Get function signature untuk parameter binding
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


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key dari prefix dan arguments
    
    Args:
        prefix: Prefix untuk cache key
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Generated cache key
    """
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    # Add keyword arguments (sorted untuk consistency)
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float, bool)):
            key_parts.append(f"{key}:{value}")
        else:
            key_parts.append(f"{key}:{hash(str(value))}")
    
    return ":".join(key_parts)

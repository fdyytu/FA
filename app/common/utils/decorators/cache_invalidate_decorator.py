"""
Cache Invalidate Decorator
Decorator untuk invalidasi cache berdasarkan pattern
"""

import functools
import inspect
import logging
from typing import Union, Callable

logger = logging.getLogger(__name__)


def cache_invalidate(
    key_patterns: Union[str, list],
    cache_type: str = "default"
):
    """
    Decorator untuk invalidate cache setelah function execution
    
    Args:
        key_patterns: Pattern atau list pattern untuk cache keys yang akan di-invalidate
        cache_type: Tipe cache yang digunakan
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            try:
                from app.cache.managers.cache_manager import cache_manager
                
                cache_service = await cache_manager.get_cache_service(cache_type)
                
                patterns = key_patterns if isinstance(key_patterns, list) else [key_patterns]
                
                for pattern in patterns:
                    try:
                        # Format pattern dengan args jika diperlukan
                        if '{' in pattern and '}' in pattern:
                            # Buat mapping dari args dan kwargs
                            sig = inspect.signature(func)
                            bound_args = sig.bind(*args, **kwargs)
                            bound_args.apply_defaults()
                            
                            formatted_pattern = pattern.format(**bound_args.arguments)
                        else:
                            formatted_pattern = pattern
                        
                        await cache_service.clear(formatted_pattern)
                        logger.debug(f"Invalidated cache pattern: {formatted_pattern}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to invalidate cache pattern {pattern}: {e}")
                        
            except Exception as e:
                logger.error(f"Cache invalidation error in {func.__name__}: {e}")
            
            return result
        
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

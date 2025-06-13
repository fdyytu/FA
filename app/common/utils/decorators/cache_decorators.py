"""
Cache related decorators
Decorators untuk caching function results
"""

import logging
from typing import Callable
from functools import wraps

logger = logging.getLogger(__name__)


def cache_result(key_template: str, expire_seconds: int = 300):
    """
    Decorator untuk caching function results
    
    Args:
        key_template: Template untuk cache key (support format strings)
        expire_seconds: Cache expiration time
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            try:
                # Combine args dan kwargs untuk key generation
                key_data = {
                    'args': args,
                    'kwargs': kwargs,
                    'func_name': func.__name__
                }
                cache_key = key_template.format(**key_data, **kwargs)
            except (KeyError, ValueError):
                # Fallback ke simple key jika template gagal
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
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
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                await cache_service.set(cache_key, result, expire_seconds)
                logger.debug(f"Cached result for {func.__name__}: {cache_key}")
            except Exception as e:
                logger.warning(f"Cache set failed for {func.__name__}: {e}")
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(key_pattern: str):
    """
    Decorator untuk invalidate cache setelah function execution
    
    Args:
        key_pattern: Pattern untuk cache keys yang akan di-invalidate
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function first
            result = await func(*args, **kwargs)
            
            # Then invalidate cache
            try:
                from app.core.container import get_service
                from app.core.interfaces import ICacheService
                
                cache_service = get_service(ICacheService)
                
                # Generate invalidation key
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
            
            return result
        
        return wrapper
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
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            
            # Check if result is cached
            if key in cache:
                # Move to end (LRU)
                cache_order.remove(key)
                cache_order.append(key)
                return cache[key]
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache[key] = result
            cache_order.append(key)
            
            # Remove oldest if cache is full
            if len(cache) > maxsize:
                oldest_key = cache_order.pop(0)
                del cache[oldest_key]
            
            return result
        
        # Add cache management methods
        wrapper.cache_clear = lambda: cache.clear() or cache_order.clear()
        wrapper.cache_info = lambda: {
            'hits': len([k for k in cache_order if k in cache]),
            'misses': len(cache_order) - len([k for k in cache_order if k in cache]),
            'maxsize': maxsize,
            'currsize': len(cache)
        }
        
        return wrapper
    return decorator

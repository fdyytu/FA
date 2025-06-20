"""
Memoize Decorator
Simple memoization decorator untuk function results
"""

import functools
import logging
from typing import Callable

logger = logging.getLogger(__name__)


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

"""
Cache Module
Sistem cache untuk PPOB API dengan implementasi SOLID principles

Fitur:
- Redis cache dengan fallback ke memory cache
- Domain-specific cache managers
- Cache decorators untuk DRY principle
- Health monitoring dan statistics
- Automatic TTL management
"""

from app.cache.managers.cache_manager import cache_manager
from app.cache.managers.ppob_cache_manager import ppob_cache_manager
from app.cache.decorators.cache_decorators import (
    cache_result, 
    cache_invalidate, 
    cache_key_from_args,
    CacheHelper
)

__all__ = [
    "cache_manager",
    "ppob_cache_manager", 
    "cache_result",
    "cache_invalidate",
    "cache_key_from_args",
    "CacheHelper"
]

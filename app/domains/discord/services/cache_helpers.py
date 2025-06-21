"""
Discord Cache Helpers - Utility functions untuk caching operations
"""
from typing import Any, Optional
from .discord_cache import discord_cache

def delete_cache(key: str) -> bool:
    """Delete cached data"""
    try:
        if discord_cache.redis_client:
            return bool(discord_cache.redis_client.delete(f"discord:{key}"))
        else:
            return discord_cache._memory_cache.pop(key, None) is not None
    except Exception:
        return False

def clear_bot_cache(bot_id: str) -> bool:
    """Clear semua cache untuk bot tertentu"""
    keys = [f"bot_status_{bot_id}", f"bot_config_{bot_id}", f"bot_metrics_{bot_id}"]
    return all(delete_cache(key) for key in keys)

def cache_bot_status(bot_id: str, status: dict, ttl: int = 60) -> bool:
    """Cache status bot dengan TTL 1 menit"""
    return discord_cache.set(f"bot_status_{bot_id}", status, ttl)

def get_bot_status(bot_id: str) -> Optional[dict]:
    """Get cached bot status"""
    return discord_cache.get(f"bot_status_{bot_id}")

def cache_command_logs(user_id: str, logs: list, ttl: int = 300) -> bool:
    """Cache command logs untuk user dengan TTL 5 menit"""
    return discord_cache.set(f"logs_{user_id}", logs, ttl)

def get_cached_logs(user_id: str) -> Optional[list]:
    """Get cached command logs untuk user"""
    return discord_cache.get(f"logs_{user_id}")

def invalidate_user_cache(user_id: str) -> bool:
    """Invalidate semua cache untuk user tertentu"""
    keys = [f"logs_{user_id}", f"user_metrics_{user_id}"]
    return all(delete_cache(key) for key in keys)

def cache_metrics(key: str, metrics: dict, ttl: int = 120) -> bool:
    """Cache metrics dengan TTL 2 menit"""
    return discord_cache.set(f"metrics_{key}", metrics, ttl)

def get_cached_metrics(key: str) -> Optional[dict]:
    """Get cached metrics"""
    return discord_cache.get(f"metrics_{key}")

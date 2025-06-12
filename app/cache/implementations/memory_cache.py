"""
Memory Cache Service Implementation
Implementasi in-memory cache sebagai fallback ketika Redis tidak tersedia
"""

import asyncio
from typing import Any, Optional, Union, Dict
from datetime import datetime, timedelta
import logging
from app.cache.interfaces.cache_interfaces import ICacheService

logger = logging.getLogger(__name__)


class MemoryCacheItem:
    """Item cache dengan TTL support"""
    
    def __init__(self, value: Any, ttl: Optional[Union[int, timedelta]] = None):
        self.value = value
        self.created_at = datetime.now()
        
        if ttl is None:
            self.expires_at = None
        elif isinstance(ttl, timedelta):
            self.expires_at = self.created_at + ttl
        else:
            self.expires_at = self.created_at + timedelta(seconds=ttl)
    
    def is_expired(self) -> bool:
        """Cek apakah item sudah expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class MemoryCacheService(ICacheService):
    """
    In-memory cache implementation
    Mengikuti Single Responsibility Principle - hanya menangani memory operations
    """
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, MemoryCacheItem] = {}
        self._max_size = max_size
        self._lock = asyncio.Lock()
    
    async def _cleanup_expired(self):
        """Bersihkan item yang sudah expired"""
        expired_keys = []
        for key, item in self._cache.items():
            if item.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
    
    async def _ensure_capacity(self):
        """Pastikan cache tidak melebihi max_size"""
        if len(self._cache) >= self._max_size:
            # Hapus 20% item tertua (LRU-like behavior)
            items_to_remove = int(self._max_size * 0.2)
            sorted_items = sorted(
                self._cache.items(), 
                key=lambda x: x[1].created_at
            )
            
            for key, _ in sorted_items[:items_to_remove]:
                del self._cache[key]
    
    async def get(self, key: str) -> Optional[Any]:
        """Ambil data dari memory cache"""
        async with self._lock:
            await self._cleanup_expired()
            
            item = self._cache.get(key)
            if item is None:
                return None
            
            if item.is_expired():
                del self._cache[key]
                return None
            
            return item.value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Simpan data ke memory cache"""
        try:
            async with self._lock:
                await self._cleanup_expired()
                await self._ensure_capacity()
                
                self._cache[key] = MemoryCacheItem(value, ttl)
                return True
                
        except Exception as e:
            logger.error(f"Error setting memory cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Hapus data dari memory cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Cek apakah key ada di memory cache"""
        async with self._lock:
            await self._cleanup_expired()
            
            item = self._cache.get(key)
            if item is None:
                return False
            
            if item.is_expired():
                del self._cache[key]
                return False
            
            return True
    
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Hapus data dari memory cache"""
        try:
            async with self._lock:
                if pattern:
                    # Simple pattern matching dengan wildcard
                    import fnmatch
                    keys_to_delete = []
                    for key in self._cache.keys():
                        if fnmatch.fnmatch(key, pattern):
                            keys_to_delete.append(key)
                    
                    for key in keys_to_delete:
                        del self._cache[key]
                else:
                    # Hapus semua data
                    self._cache.clear()
                
                return True
                
        except Exception as e:
            logger.error(f"Error clearing memory cache with pattern {pattern}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Cek kesehatan memory cache"""
        async with self._lock:
            await self._cleanup_expired()
            
            return {
                "status": "healthy",
                "type": "memory",
                "total_items": len(self._cache),
                "max_size": self._max_size,
                "usage_percentage": (len(self._cache) / self._max_size) * 100
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Ambil statistik cache"""
        async with self._lock:
            await self._cleanup_expired()
            
            expired_count = 0
            for item in self._cache.values():
                if item.is_expired():
                    expired_count += 1
            
            return {
                "total_items": len(self._cache),
                "expired_items": expired_count,
                "max_size": self._max_size,
                "usage_percentage": (len(self._cache) / self._max_size) * 100
            }

"""
Cache interfaces untuk implementasi SOLID principles
- Interface Segregation: Interface terpisah untuk berbagai concern
- Dependency Inversion: Bergantung pada abstraksi, bukan implementasi konkret
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union
from datetime import timedelta


class ICacheService(ABC):
    """Interface utama untuk cache service operations"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Ambil data dari cache berdasarkan key"""
        pass
    
    @abstractmethod
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Simpan data ke cache dengan TTL opsional"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Hapus data dari cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Cek apakah key ada di cache"""
        pass
    
    @abstractmethod
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Hapus semua data atau berdasarkan pattern"""
        pass


class ICacheManager(ABC):
    """Interface untuk cache manager yang mengelola multiple cache instances"""
    
    @abstractmethod
    async def get_cache_service(self, cache_type: str = "default") -> ICacheService:
        """Ambil cache service berdasarkan type"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Cek kesehatan cache services"""
        pass


class ICacheSerializer(ABC):
    """Interface untuk serialization cache data"""
    
    @abstractmethod
    def serialize(self, data: Any) -> str:
        """Serialize data untuk disimpan di cache"""
        pass
    
    @abstractmethod
    def deserialize(self, data: str) -> Any:
        """Deserialize data dari cache"""
        pass


class ICacheKeyGenerator(ABC):
    """Interface untuk generate cache keys"""
    
    @abstractmethod
    def generate_key(
        self, 
        prefix: str, 
        *args, 
        **kwargs
    ) -> str:
        """Generate cache key dengan prefix dan parameters"""
        pass
    
    @abstractmethod
    def generate_pattern(self, prefix: str, pattern: str = "*") -> str:
        """Generate pattern untuk cache key matching"""
        pass

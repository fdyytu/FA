"""
PPOB Cache Manager
Domain-specific cache manager untuk PPOB operations
Mengikuti Single Responsibility Principle - hanya menangani PPOB caching
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import timedelta
from app.cache.managers.cache_manager import cache_manager
from app.cache.decorators.cache_decorators import cache_result, cache_invalidate, CacheHelper
from app.domains.ppob.models.ppob import PPOBProduct, PPOBCategory

logger = logging.getLogger(__name__)


class PPOBCacheManager:
    """
    Cache manager khusus untuk PPOB operations
    Mengikuti Domain-Driven Design - cache logic terpisah per domain
    """
    
    def __init__(self):
        self.cache_type = "default"
        self.default_ttl = timedelta(minutes=30)  # 30 menit default TTL
        self.product_ttl = timedelta(hours=1)     # 1 jam untuk product cache
        self.inquiry_ttl = timedelta(minutes=5)   # 5 menit untuk inquiry cache
    
    async def get_products_by_category(
        self, 
        category: PPOBCategory,
        fetch_func: callable
    ) -> List[PPOBProduct]:
        """
        Cache products berdasarkan kategori
        """
        key_generator = cache_manager.get_key_generator()
        cache_key = key_generator.generate_key("ppob:products", category.value)
        
        return await CacheHelper.get_or_set(
            key=cache_key,
            factory_func=lambda: fetch_func(category),
            ttl=self.product_ttl,
            cache_type=self.cache_type
        )
    
    async def get_product_by_code(
        self,
        product_code: str,
        fetch_func: callable
    ) -> Optional[PPOBProduct]:
        """
        Cache product berdasarkan kode
        """
        key_generator = cache_manager.get_key_generator()
        cache_key = key_generator.generate_key("ppob:product", product_code)
        
        return await CacheHelper.get_or_set(
            key=cache_key,
            factory_func=lambda: fetch_func(product_code),
            ttl=self.product_ttl,
            cache_type=self.cache_type
        )
    
    async def cache_inquiry_result(
        self,
        category: PPOBCategory,
        customer_number: str,
        inquiry_data: Dict[str, Any]
    ) -> bool:
        """
        Cache hasil inquiry
        """
        try:
            cache_service = await cache_manager.get_cache_service(self.cache_type)
            key_generator = cache_manager.get_key_generator()
            
            cache_key = key_generator.generate_key(
                "ppob:inquiry", 
                category.value, 
                customer_number
            )
            
            return await cache_service.set(
                cache_key, 
                inquiry_data, 
                self.inquiry_ttl
            )
            
        except Exception as e:
            logger.error(f"Error caching inquiry result: {e}")
            return False
    
    async def get_cached_inquiry(
        self,
        category: PPOBCategory,
        customer_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Ambil cached inquiry result
        """
        try:
            cache_service = await cache_manager.get_cache_service(self.cache_type)
            key_generator = cache_manager.get_key_generator()
            
            cache_key = key_generator.generate_key(
                "ppob:inquiry", 
                category.value, 
                customer_number
            )
            
            return await cache_service.get(cache_key)
            
        except Exception as e:
            logger.error(f"Error getting cached inquiry: {e}")
            return None
    
    async def invalidate_product_cache(
        self, 
        category: Optional[PPOBCategory] = None,
        product_code: Optional[str] = None
    ) -> bool:
        """
        Invalidate product cache
        """
        try:
            key_generator = cache_manager.get_key_generator()
            
            if product_code:
                # Invalidate specific product
                pattern = key_generator.generate_pattern("ppob:product", product_code)
            elif category:
                # Invalidate category products
                pattern = key_generator.generate_pattern("ppob:products", category.value)
            else:
                # Invalidate all products
                pattern = key_generator.generate_pattern("ppob:product*")
            
            return await CacheHelper.invalidate_pattern(pattern, self.cache_type)
            
        except Exception as e:
            logger.error(f"Error invalidating product cache: {e}")
            return False
    
    async def invalidate_inquiry_cache(
        self,
        category: Optional[PPOBCategory] = None,
        customer_number: Optional[str] = None
    ) -> bool:
        """
        Invalidate inquiry cache
        """
        try:
            key_generator = cache_manager.get_key_generator()
            
            if category and customer_number:
                # Invalidate specific inquiry
                pattern = key_generator.generate_pattern(
                    "ppob:inquiry", 
                    f"{category.value}:{customer_number}"
                )
            elif category:
                # Invalidate all inquiry untuk category
                pattern = key_generator.generate_pattern(
                    "ppob:inquiry", 
                    f"{category.value}:*"
                )
            else:
                # Invalidate all inquiry
                pattern = key_generator.generate_pattern("ppob:inquiry*")
            
            return await CacheHelper.invalidate_pattern(pattern, self.cache_type)
            
        except Exception as e:
            logger.error(f"Error invalidating inquiry cache: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Ambil statistik cache untuk PPOB
        """
        try:
            cache_service = await cache_manager.get_cache_service(self.cache_type)
            key_generator = cache_manager.get_key_generator()
            
            # Hitung jumlah keys untuk setiap pattern
            patterns = {
                "products": key_generator.generate_pattern("ppob:products*"),
                "product_details": key_generator.generate_pattern("ppob:product:*"),
                "inquiries": key_generator.generate_pattern("ppob:inquiry*")
            }
            
            stats = {}
            for name, pattern in patterns.items():
                # Untuk Redis, kita bisa count keys
                # Untuk Memory cache, ini akan lebih kompleks
                try:
                    if hasattr(cache_service, '_redis_client'):
                        client = await cache_service._get_redis_client()
                        keys = await client.keys(pattern)
                        stats[name] = len(keys)
                    else:
                        # Fallback untuk memory cache
                        stats[name] = "N/A"
                except:
                    stats[name] = "N/A"
            
            return {
                "ppob_cache_stats": stats,
                "ttl_settings": {
                    "default_ttl": str(self.default_ttl),
                    "product_ttl": str(self.product_ttl),
                    "inquiry_ttl": str(self.inquiry_ttl)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting PPOB cache stats: {e}")
            return {"error": str(e)}


# Global PPOB cache manager instance
ppob_cache_manager = PPOBCacheManager()

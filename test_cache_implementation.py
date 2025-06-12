"""
Test Cache Implementation
Test untuk memastikan cache berfungsi dengan baik
"""

import asyncio
from datetime import timedelta
from app.cache.managers.cache_manager import cache_manager
from app.cache.managers.ppob_cache_manager import ppob_cache_manager
from app.cache.decorators.cache_decorators import cache_result, CacheHelper


async def test_cache_basic_operations():
    """Test basic cache operations"""
    print("Testing basic cache operations...")
    
    # Initialize cache
    await cache_manager.initialize()
    
    # Get cache service
    cache_service = await cache_manager.get_cache_service()
    
    # Test set and get
    test_key = "test:basic:key"
    test_value = {"message": "Hello Cache!", "number": 42}
    
    # Set value
    result = await cache_service.set(test_key, test_value, ttl=60)
    assert result == True, "Failed to set cache value"
    print("✓ Cache set operation successful")
    
    # Get value
    cached_value = await cache_service.get(test_key)
    assert cached_value == test_value, "Cached value doesn't match original"
    print("✓ Cache get operation successful")
    
    # Test exists
    exists = await cache_service.exists(test_key)
    assert exists == True, "Cache key should exist"
    print("✓ Cache exists check successful")
    
    # Test delete
    deleted = await cache_service.delete(test_key)
    assert deleted == True, "Failed to delete cache key"
    print("✓ Cache delete operation successful")
    
    # Verify deletion
    cached_value = await cache_service.get(test_key)
    assert cached_value is None, "Cache value should be None after deletion"
    print("✓ Cache deletion verification successful")


async def test_cache_ttl():
    """Test cache TTL functionality"""
    print("\nTesting cache TTL...")
    
    cache_service = await cache_manager.get_cache_service()
    
    # Set value with short TTL
    test_key = "test:ttl:key"
    test_value = "TTL Test Value"
    
    result = await cache_service.set(test_key, test_value, ttl=2)  # 2 seconds
    assert result == True, "Failed to set cache value with TTL"
    print("✓ Cache set with TTL successful")
    
    # Immediately check value exists
    cached_value = await cache_service.get(test_key)
    assert cached_value == test_value, "Value should exist immediately"
    print("✓ Value exists immediately after set")
    
    # Wait for TTL to expire
    print("Waiting for TTL to expire...")
    await asyncio.sleep(3)
    
    # Check value is expired
    cached_value = await cache_service.get(test_key)
    assert cached_value is None, "Value should be None after TTL expiry"
    print("✓ Value expired after TTL")


async def test_cache_decorator():
    """Test cache decorator functionality"""
    print("\nTesting cache decorator...")
    
    call_count = 0
    
    @cache_result(ttl=60, key_prefix="test:decorator")
    async def expensive_function(param1: str, param2: int):
        nonlocal call_count
        call_count += 1
        return f"Result: {param1}-{param2}, Call: {call_count}"
    
    # First call - should execute function
    result1 = await expensive_function("test", 123)
    assert call_count == 1, "Function should be called once"
    print(f"✓ First call result: {result1}")
    
    # Second call with same params - should use cache
    result2 = await expensive_function("test", 123)
    assert call_count == 1, "Function should not be called again (cached)"
    assert result1 == result2, "Results should be identical"
    print(f"✓ Second call result (cached): {result2}")
    
    # Third call with different params - should execute function
    result3 = await expensive_function("different", 456)
    assert call_count == 2, "Function should be called again with different params"
    print(f"✓ Third call result (different params): {result3}")


async def test_ppob_cache_manager():
    """Test PPOB-specific cache manager"""
    print("\nTesting PPOB cache manager...")
    
    # Mock function to simulate database fetch
    def mock_fetch_products(category):
        return [
            {"id": 1, "name": f"Product 1 for {category.value}", "price": 10000},
            {"id": 2, "name": f"Product 2 for {category.value}", "price": 20000}
        ]
    
    # Mock category enum
    class MockCategory:
        def __init__(self, value):
            self.value = value
    
    category = MockCategory("PULSA")
    
    # Test caching products
    products1 = await ppob_cache_manager.get_products_by_category(
        category=category,
        fetch_func=mock_fetch_products
    )
    print(f"✓ First products fetch: {len(products1)} products")
    
    # Second call should use cache (same mock function but won't be called)
    products2 = await ppob_cache_manager.get_products_by_category(
        category=category,
        fetch_func=lambda x: []  # This shouldn't be called due to cache
    )
    assert len(products2) == len(products1), "Should get same products from cache"
    print(f"✓ Second products fetch (cached): {len(products2)} products")


async def test_cache_health():
    """Test cache health check"""
    print("\nTesting cache health check...")
    
    health = await cache_manager.health_check()
    print(f"✓ Cache health status: {health.get('overall_status')}")
    
    # Print detailed health info
    for service_name, service_health in health.get('services', {}).items():
        status = service_health.get('status', 'unknown')
        print(f"  - {service_name}: {status}")


async def test_cache_helper():
    """Test cache helper functionality"""
    print("\nTesting cache helper...")
    
    call_count = 0
    
    def factory_function():
        nonlocal call_count
        call_count += 1
        return f"Factory result #{call_count}"
    
    # First call - should execute factory
    result1 = await CacheHelper.get_or_set(
        key="test:helper:key",
        factory_func=factory_function,
        ttl=60
    )
    assert call_count == 1, "Factory should be called once"
    print(f"✓ First helper call: {result1}")
    
    # Second call - should use cache
    result2 = await CacheHelper.get_or_set(
        key="test:helper:key",
        factory_func=factory_function,
        ttl=60
    )
    assert call_count == 1, "Factory should not be called again"
    assert result1 == result2, "Results should be identical"
    print(f"✓ Second helper call (cached): {result2}")


async def run_all_tests():
    """Run all cache tests"""
    print("=== CACHE IMPLEMENTATION TESTS ===\n")
    
    try:
        await test_cache_basic_operations()
        await test_cache_ttl()
        await test_cache_decorator()
        await test_ppob_cache_manager()
        await test_cache_health()
        await test_cache_helper()
        
        print("\n=== ALL TESTS PASSED! ===")
        print("Cache implementation is working correctly.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    finally:
        # Cleanup
        await cache_manager.close_all()
        print("\n✓ Cache connections closed")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

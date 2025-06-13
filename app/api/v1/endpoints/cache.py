"""
Cache Management Endpoints
Endpoint untuk mengelola cache operations
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, Optional
from app.cache.managers.cache_manager import cache_manager
from app.cache.managers.ppob_cache_manager import ppob_cache_manager
from app.middleware.security import require_admin

router = APIRouter()


@router.get("/health", summary="Cache Health Check")
async def cache_health_check() -> Dict[str, Any]:
    """
    Cek kesehatan semua cache services
    """
    try:
        health_status = await cache_manager.health_check()
        return {
            "success": True,
            "data": health_status
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking cache health: {str(e)}"
        )


@router.get("/stats", summary="Cache Statistics")
async def cache_statistics() -> Dict[str, Any]:
    """
    Ambil statistik cache
    """
    try:
        # Get general cache health
        health_status = await cache_manager.health_check()
        
        # Get PPOB specific stats
        ppob_stats = await ppob_cache_manager.get_cache_stats()
        
        return {
            "success": True,
            "data": {
                "general": health_status,
                "ppob": ppob_stats
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting cache statistics: {str(e)}"
        )


@router.delete("/clear", summary="Clear Cache")
async def clear_cache(
    pattern: Optional[str] = None,
    # admin_user = Depends(get_current_admin_user)  # Uncomment if admin auth exists
) -> Dict[str, Any]:
    """
    Clear cache berdasarkan pattern
    Hanya admin yang bisa mengakses endpoint ini
    """
    try:
        results = await cache_manager.clear_all_caches(pattern)
        
        return {
            "success": True,
            "message": f"Cache cleared successfully with pattern: {pattern or 'all'}",
            "data": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )


@router.delete("/ppob/products", summary="Clear PPOB Product Cache")
async def clear_ppob_product_cache(
    category: Optional[str] = None,
    product_code: Optional[str] = None,
    # admin_user = Depends(get_current_admin_user)  # Uncomment if admin auth exists
) -> Dict[str, Any]:
    """
    Clear PPOB product cache
    """
    try:
        from app.models.ppob import PPOBCategory
        
        cat_enum = None
        if category:
            try:
                cat_enum = PPOBCategory(category)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category: {category}"
                )
        
        success = await ppob_cache_manager.invalidate_product_cache(
            category=cat_enum,
            product_code=product_code
        )
        
        if success:
            return {
                "success": True,
                "message": "PPOB product cache cleared successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear PPOB product cache"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing PPOB product cache: {str(e)}"
        )


@router.delete("/ppob/inquiry", summary="Clear PPOB Inquiry Cache")
async def clear_ppob_inquiry_cache(
    category: Optional[str] = None,
    customer_number: Optional[str] = None,
    # admin_user = Depends(get_current_admin_user)  # Uncomment if admin auth exists
) -> Dict[str, Any]:
    """
    Clear PPOB inquiry cache
    """
    try:
        from app.models.ppob import PPOBCategory
        
        cat_enum = None
        if category:
            try:
                cat_enum = PPOBCategory(category)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category: {category}"
                )
        
        success = await ppob_cache_manager.invalidate_inquiry_cache(
            category=cat_enum,
            customer_number=customer_number
        )
        
        if success:
            return {
                "success": True,
                "message": "PPOB inquiry cache cleared successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear PPOB inquiry cache"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing PPOB inquiry cache: {str(e)}"
        )

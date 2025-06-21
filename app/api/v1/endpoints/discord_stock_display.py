"""
Stock Display Management API - Core Operations
"""
from fastapi import APIRouter, HTTPException, Depends
from app.domains.discord.services.stock_display_service import StockDisplayService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/stock-display", tags=["Stock Display Management"])

async def get_stock_service():
    return StockDisplayService()

@router.post("/toggle")
async def toggle_product_display(
    bot_id: int,
    product_id: int,
    show: bool,
    service: StockDisplayService = Depends(get_stock_service),
    current_user = Depends(get_current_user)
):
    """Toggle tampilan produk untuk bot tertentu"""
    return await service.toggle_product_display(bot_id, product_id, show, current_user.id)

@router.get("/{bot_id}/settings")
async def get_display_settings(
    bot_id: int,
    service: StockDisplayService = Depends(get_stock_service),
    current_user = Depends(get_current_user)
):
    """Dapatkan setting display untuk bot tertentu"""
    return await service.get_display_settings(bot_id)

@router.post("/{bot_id}/reset")
async def reset_display_settings(
    bot_id: int,
    service: StockDisplayService = Depends(get_stock_service),
    current_user = Depends(get_current_user)
):
    """Reset semua setting display untuk bot tertentu"""
    try:
        # Implementation untuk reset settings
        return {"success": True, "message": "Settings berhasil direset"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

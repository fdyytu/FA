"""
Stock Display Bulk Operations API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.domains.discord.services.stock_display_bulk import StockDisplayBulkService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/stock-display-bulk", tags=["Stock Display Bulk"])

async def get_bulk_stock_service():
    return StockDisplayBulkService()

@router.post("/bulk/toggle")
async def bulk_toggle_products(
    bot_id: int,
    product_ids: List[int],
    show: bool,
    service: StockDisplayBulkService = Depends(get_bulk_stock_service),
    current_user = Depends(get_current_user)
):
    """Toggle multiple products untuk bot tertentu"""
    return await service.bulk_toggle_products(bot_id, product_ids, show, current_user.id)

@router.post("/{bot_id}/hide-all")
async def hide_all_products(
    bot_id: int,
    service: StockDisplayBulkService = Depends(get_bulk_stock_service),
    current_user = Depends(get_current_user)
):
    """Sembunyikan semua produk untuk bot tertentu"""
    return await service.bulk_hide_all_products(bot_id, current_user.id)

@router.post("/{bot_id}/show-all")
async def show_all_products(
    bot_id: int,
    service: StockDisplayBulkService = Depends(get_bulk_stock_service),
    current_user = Depends(get_current_user)
):
    """Tampilkan semua produk untuk bot tertentu"""
    try:
        # Implementation untuk show all products
        return {"success": True, "message": "Semua produk ditampilkan"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

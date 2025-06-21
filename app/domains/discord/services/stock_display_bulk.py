"""
Stock Display Bulk Operations
"""
from typing import Dict, Any, List
from app.domains.discord.services.stock_display_service import StockDisplayService
from app.core.logging import get_logger

logger = get_logger(__name__)

class StockDisplayBulkService:
    def __init__(self):
        self.stock_service = StockDisplayService()
    
    async def bulk_toggle_products(
        self, bot_id: int, product_ids: List[int], show: bool, user_id: int
    ) -> Dict[str, Any]:
        """Toggle multiple products untuk bot tertentu"""
        results = {"success": [], "failed": []}
        
        for product_id in product_ids:
            result = await self.stock_service.toggle_product_display(
                bot_id, product_id, show, user_id
            )
            if result["success"]:
                results["success"].append(product_id)
            else:
                results["failed"].append({"product_id": product_id, "error": result["error"]})
        
        logger.info(f"Bulk toggle: {len(results['success'])} success, {len(results['failed'])} failed")
        return results
    
    async def bulk_hide_all_products(self, bot_id: int, user_id: int) -> Dict[str, Any]:
        """Sembunyikan semua produk untuk bot tertentu"""
        try:
            settings = await self.stock_service.get_display_settings(bot_id)
            product_ids = list(settings.keys())
            
            if not product_ids:
                return {"success": True, "message": "Tidak ada produk untuk disembunyikan"}
            
            result = await self.bulk_toggle_products(bot_id, product_ids, False, user_id)
            return {
                "success": True,
                "hidden_count": len(result["success"]),
                "failed_count": len(result["failed"]),
                "details": result
            }
        except Exception as e:
            logger.error(f"Error bulk hide: {str(e)}")
            return {"success": False, "error": str(e)}

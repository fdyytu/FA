"""
Stock Display Service - Core Operations
"""
from typing import Dict, Any
from app.domains.discord.services.discord_bot_service import DiscordBotService
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

class StockDisplayService:
    def __init__(self):
        self.bot_service = DiscordBotService()
        self._display_settings = {}
    
    async def toggle_product_display(
        self, bot_id: int, product_id: int, show: bool, user_id: int
    ) -> Dict[str, Any]:
        """Toggle tampilan produk untuk bot tertentu"""
        try:
            key = f"{bot_id}_{product_id}"
            self._display_settings[key] = show
            
            await self._update_bot_display_config(bot_id, product_id, show, user_id)
            
            status = "ditampilkan" if show else "disembunyikan"
            logger.info(f"Product {product_id} {status} untuk bot {bot_id}")
            
            return {
                "success": True,
                "bot_id": bot_id,
                "product_id": product_id,
                "display": show,
                "message": f"Produk berhasil {status}"
            }
        except Exception as e:
            logger.error(f"Error toggle display: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_display_settings(self, bot_id: int) -> Dict[int, bool]:
        """Dapatkan setting display untuk bot tertentu"""
        settings = {}
        for key, value in self._display_settings.items():
            if key.startswith(f"{bot_id}_"):
                product_id = int(key.split("_")[1])
                settings[product_id] = value
        return settings
    
    async def _update_bot_display_config(self, bot_id: int, product_id: int, show: bool, user_id: int):
        """Update konfigurasi display di bot"""
        pass

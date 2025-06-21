"""
Bulk Operations Service - Core Operations
"""
import asyncio
from typing import List, Dict, Any
from app.domains.discord.services.discord_bot_service import DiscordBotService
from app.core.logging import get_logger

logger = get_logger(__name__)

class BulkOperationsService:
    def __init__(self):
        self.bot_service = DiscordBotService()
    
    async def bulk_start_bots(self, bot_ids: List[int], user_id: int) -> Dict[str, Any]:
        """Start multiple bots secara bersamaan"""
        results = {"success": [], "failed": []}
        
        tasks = [self._start_single_bot(bot_id, user_id) for bot_id in bot_ids]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, response in enumerate(responses):
            bot_id = bot_ids[i]
            if isinstance(response, Exception):
                results["failed"].append({"bot_id": bot_id, "error": str(response)})
            else:
                results["success"].append({"bot_id": bot_id, "status": response})
        
        logger.info(f"Bulk start: {len(results['success'])} success, {len(results['failed'])} failed")
        return results
    
    async def bulk_stop_bots(self, bot_ids: List[int], user_id: int) -> Dict[str, Any]:
        """Stop multiple bots secara bersamaan"""
        results = {"success": [], "failed": []}
        
        for bot_id in bot_ids:
            try:
                await self.bot_service.stop_bot(bot_id, user_id)
                results["success"].append({"bot_id": bot_id, "status": "stopped"})
            except Exception as e:
                results["failed"].append({"bot_id": bot_id, "error": str(e)})
        
        return results
    
    async def _start_single_bot(self, bot_id: int, user_id: int):
        """Helper untuk start single bot"""
        return await self.bot_service.start_bot(bot_id, user_id)

"""
Bulk Messaging Service untuk Discord Bot
"""
import asyncio
from typing import List, Dict, Any
from app.domains.discord.services.discord_bot_service import DiscordBotService
from app.core.logging import get_logger

logger = get_logger(__name__)

class BulkMessagingService:
    def __init__(self):
        self.bot_service = DiscordBotService()
    
    async def bulk_send_message(
        self, bot_ids: List[int], channel_id: str, message: str, user_id: int
    ) -> Dict[str, Any]:
        """Kirim pesan ke multiple bots secara bersamaan"""
        results = {"success": [], "failed": []}
        
        tasks = [self._send_message_single_bot(bot_id, channel_id, message, user_id) 
                for bot_id in bot_ids]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, response in enumerate(responses):
            bot_id = bot_ids[i]
            if isinstance(response, Exception):
                results["failed"].append({"bot_id": bot_id, "error": str(response)})
            else:
                results["success"].append({"bot_id": bot_id, "message_id": response})
        
        logger.info(f"Bulk message: {len(results['success'])} sent, {len(results['failed'])} failed")
        return results
    
    async def bulk_restart_bots(self, bot_ids: List[int], user_id: int) -> Dict[str, Any]:
        """Restart multiple bots secara bersamaan"""
        results = {"success": [], "failed": []}
        
        for bot_id in bot_ids:
            try:
                await self.bot_service.restart_bot(bot_id, user_id)
                results["success"].append({"bot_id": bot_id, "status": "restarted"})
            except Exception as e:
                results["failed"].append({"bot_id": bot_id, "error": str(e)})
        
        return results
    
    async def _send_message_single_bot(self, bot_id: int, channel_id: str, message: str, user_id: int):
        """Helper untuk kirim pesan ke single bot"""
        return await self.bot_service.send_message(bot_id, channel_id, message, user_id)

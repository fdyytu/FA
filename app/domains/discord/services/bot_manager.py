"""
Discord Bot Manager
Manager untuk lifecycle dan monitoring Discord bot
"""
import os
import logging
from typing import Dict, Any, Optional
from app.domains.discord.services.discord_bot_service import bot_service

logger = logging.getLogger(__name__)


class DiscordBotManager:
    """Manager untuk mengelola lifecycle Discord bot"""
    
    def __init__(self):
        self.bot_service = bot_service
        self.is_initialized = False
        
    async def initialize_from_env(self) -> bool:
        """Initialize bot dari environment variables"""
        try:
            discord_token = os.getenv("DISCORD_TOKEN")
            if not discord_token:
                logger.warning("DISCORD_TOKEN tidak ditemukan di environment variables")
                return False
            
            command_prefix = os.getenv("DISCORD_COMMAND_PREFIX", "!")
            
            success = await self.bot_service.initialize(
                token=discord_token,
                command_prefix=command_prefix
            )
            
            if success:
                self.is_initialized = True
                logger.info("Discord bot manager initialized successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing bot manager: {e}")
            return False
    
    async def start_bot(self) -> bool:
        """Start Discord bot"""
        try:
            if not self.is_initialized:
                logger.error("Bot manager not initialized")
                return False
            
            return await self.bot_service.start()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            return False
    
    async def stop_bot(self) -> bool:
        """Stop Discord bot"""
        try:
            return await self.bot_service.stop()
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return False
    
    async def restart_bot(self) -> bool:
        """Restart Discord bot"""
        try:
            return await self.bot_service.restart()
            
        except Exception as e:
            logger.error(f"Error restarting bot: {e}")
            return False
    
    def get_bot_status(self) -> Dict[str, Any]:
        """Get comprehensive bot status"""
        try:
            base_status = self.bot_service.get_status()
            
            return {
                **base_status,
                "manager_initialized": self.is_initialized,
                "token_configured": bool(os.getenv("DISCORD_TOKEN")),
                "environment": {
                    "command_prefix": os.getenv("DISCORD_COMMAND_PREFIX", "!"),
                    "guild_id": os.getenv("DISCORD_GUILD_ID"),
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "manager_initialized": self.is_initialized
            }
    
    async def send_notification(self, channel_id: int, message: str) -> bool:
        """Send notification to Discord channel"""
        try:
            return await self.bot_service.send_message(channel_id, message)
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def is_bot_healthy(self) -> bool:
        """Check if bot is healthy"""
        try:
            status = self.get_bot_status()
            return (
                status.get("is_running", False) and
                status.get("status") == "online" and
                self.is_initialized
            )
            
        except Exception as e:
            logger.error(f"Error checking bot health: {e}")
            return False


# Global bot manager instance
bot_manager = DiscordBotManager()

"""
Discord Bot Service - Main orchestrator
Mengelola Discord Bot dengan prinsip SOLID dan modular architecture
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.domains.discord.services.bot.bot_core import DiscordBotCore
from app.domains.discord.services.bot.bot_events import DiscordBotEvents
from app.domains.discord.services.commands.slash_commands import DiscordSlashCommands
from app.domains.discord.services.ui.ui_components import MainMenuView

logger = logging.getLogger(__name__)


class DiscordBotService:
    """
    Main Discord Bot Service yang mengorkestrasikan semua komponen bot
    Menggunakan composition pattern untuk modular architecture
    """
    
    def __init__(self):
        self.bot_core = DiscordBotCore()
        self.bot_events: Optional[DiscordBotEvents] = None
        self.slash_commands: Optional[DiscordSlashCommands] = None
        self.is_running = False
        
    async def initialize_bot(self, bot_id: int, db: Session):
        """Initialize Discord Bot dengan semua komponennya"""
        try:
            # Initialize core bot
            await self.bot_core.initialize_bot(bot_id, db)
            
            # Initialize events
            self.bot_events = DiscordBotEvents(
                self.bot_core.bot, 
                self.bot_core.bot_config
            )
            
            # Initialize slash commands
            self.slash_commands = DiscordSlashCommands(
                self.bot_core.bot,
                self.bot_core.bot_config
            )
            await self.slash_commands.setup_commands()
            
            logger.info("Discord bot service fully initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Discord bot service: {e}")
            raise
    
    async def start_bot(self):
        """Start the Discord bot"""
        try:
            if not self.bot_core.bot_config:
                raise ValueError("Bot not initialized")
                
            self.is_running = True
            await self.bot_core.start_bot()
            
        except Exception as e:
            logger.error(f"Error starting Discord bot service: {e}")
            self.is_running = False
            raise
    
    async def stop_bot(self):
        """Stop the Discord bot"""
        try:
            await self.bot_core.stop_bot()
            self.is_running = False
            logger.info("Discord bot service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Discord bot service: {e}")
    
    def get_bot(self):
        """Get bot instance"""
        return self.bot_core.bot
    
    def get_bot_config(self):
        """Get bot configuration"""
        return self.bot_core.bot_config
    
    def is_bot_running(self):
        """Check if bot is running"""
        return self.is_running and self.bot_core.bot and not self.bot_core.bot.is_closed()


# Factory function untuk membuat bot service
async def create_discord_bot_service(bot_id: int, db: Session) -> DiscordBotService:
    """
    Factory function untuk membuat dan menginisialisasi Discord Bot Service
    
    Args:
        bot_id: ID konfigurasi bot
        db: Database session
        
    Returns:
        DiscordBotService: Instance bot service yang sudah diinisialisasi
    """
    service = DiscordBotService()
    await service.initialize_bot(bot_id, db)
    return service

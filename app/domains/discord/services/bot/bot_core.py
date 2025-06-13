"""
Core Discord Bot functionality
Mengelola inisialisasi dan konfigurasi bot
"""

import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.discord import DiscordBot

logger = logging.getLogger(__name__)


class DiscordBotCore:
    """Core service untuk mengelola Discord Bot"""
    
    def __init__(self):
        self.bot: Optional[commands.Bot] = None
        self.bot_config: Optional[DiscordBot] = None
        self.is_running = False
        
    async def initialize_bot(self, bot_id: int, db: Session):
        """Initialize Discord Bot"""
        try:
            # Get bot configuration
            self.bot_config = db.query(DiscordBot).filter(
                DiscordBot.id == bot_id,
                DiscordBot.is_active == True
            ).first()
            
            if not self.bot_config:
                raise ValueError(f"Bot configuration not found for ID: {bot_id}")
            
            # Setup bot intents
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            intents.members = True
            
            # Create bot instance
            self.bot = commands.Bot(
                command_prefix='!',
                intents=intents,
                description="Live Stock Bot untuk Growtopia"
            )
            
            logger.info(f"Discord bot initialized for guild: {self.bot_config.guild_id}")
            
        except Exception as e:
            logger.error(f"Error initializing Discord bot: {e}")
            raise
    
    async def start_bot(self):
        """Start the Discord bot"""
        try:
            if not self.bot_config:
                raise ValueError("Bot not initialized")
                
            self.is_running = True
            await self.bot.start(self.bot_config.token)
            
        except Exception as e:
            logger.error(f"Error starting Discord bot: {e}")
            self.is_running = False
            raise
    
    async def stop_bot(self):
        """Stop the Discord bot"""
        try:
            if self.bot and not self.bot.is_closed():
                await self.bot.close()
            self.is_running = False
            logger.info("Discord bot stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Discord bot: {e}")

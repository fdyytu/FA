"""
Discord Bot Event Handlers
Mengelola semua event yang terjadi di Discord bot
"""

import discord
from discord.ext import commands, tasks
import logging
from typing import Optional

from app.infrastructure.database.database_manager import get_db
# from app.models.discord import LiveStock  # Commented out - model not found

logger = logging.getLogger(__name__)


class DiscordBotEvents:
    """Service untuk mengelola Discord Bot Events"""
    
    def __init__(self, bot: commands.Bot, bot_config):
        self.bot = bot
        self.bot_config = bot_config
        self._setup_events()
        
    def _setup_events(self):
        """Setup Discord bot events"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'{self.bot.user} has connected to Discord!')
            
            # Start live stock update task
            if not self.update_live_stock.is_running():
                self.update_live_stock.start()
            
            # Sync slash commands
            try:
                synced = await self.bot.tree.sync()
                logger.info(f"Synced {len(synced)} command(s)")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")
        
        @self.bot.event
        async def on_error(event, *args, **kwargs):
            logger.error(f"Discord bot error in {event}: {args}")
            
        @self.bot.event
        async def on_command_error(ctx, error):
            """Handle command errors"""
            if isinstance(error, commands.CommandNotFound):
                return
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("❌ Parameter yang diperlukan tidak lengkap")
            elif isinstance(error, commands.BadArgument):
                await ctx.send("❌ Parameter tidak valid")
            else:
                logger.error(f"Command error: {error}")
                await ctx.send("❌ Terjadi kesalahan saat menjalankan command")
    
    @tasks.loop(minutes=5)
    async def update_live_stock(self):
        """Update live stock data periodically"""
        try:
            # TODO: Implement live stock update when model is available
            logger.info("Live stock update task running (placeholder)")
            
        except Exception as e:
            logger.error(f"Error updating live stock: {e}")
    
    @update_live_stock.before_loop
    async def before_update_live_stock(self):
        """Wait for bot to be ready before starting the task"""
        await self.bot.wait_until_ready()

"""
Discord Bot Service
Service utama untuk mengelola Discord bot yang terintegrasi dengan backend
"""
import asyncio
import logging
from typing import Optional, Dict, Any
import discord
from discord.ext import commands
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.callbacks.discord.discord_callbacks import DiscordBotEventHandler, DiscordSlashCommandHandler

logger = logging.getLogger(__name__)


class DiscordBotService:
    """Service untuk mengelola Discord bot"""
    
    def __init__(self):
        self.bot: Optional[commands.Bot] = None
        self.is_running = False
        self.token: Optional[str] = None
        self.event_handler: Optional[DiscordBotEventHandler] = None
        self.slash_handler: Optional[DiscordSlashCommandHandler] = None
        
    async def initialize(self, token: str, command_prefix: str = "!") -> bool:
        """Initialize Discord bot"""
        try:
            self.token = token
            
            # Setup bot intents
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            intents.guilds = True
            
            # Create bot instance
            self.bot = commands.Bot(
                command_prefix=command_prefix,
                intents=intents,
                help_command=None
            )
            
            # Setup event handlers
            self.event_handler = DiscordBotEventHandler(self.bot)
            self.slash_handler = DiscordSlashCommandHandler(self.bot)
            
            # Setup additional commands
            await self._setup_commands()
            
            logger.info("Discord bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Discord bot: {e}")
            return False
    
    async def start(self) -> bool:
        """Start Discord bot"""
        try:
            if not self.bot or not self.token:
                logger.error("Bot not initialized")
                return False
            
            if self.is_running:
                logger.warning("Bot is already running")
                return True
            
            # Start bot in background task
            asyncio.create_task(self._run_bot())
            self.is_running = True
            
            logger.info("Discord bot started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Discord bot: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop Discord bot"""
        try:
            if not self.bot or not self.is_running:
                logger.warning("Bot is not running")
                return True
            
            await self.bot.close()
            self.is_running = False
            
            logger.info("Discord bot stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Discord bot: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart Discord bot"""
        try:
            await self.stop()
            await asyncio.sleep(2)  # Wait a bit before restart
            return await self.start()
            
        except Exception as e:
            logger.error(f"Error restarting Discord bot: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        if not self.bot:
            return {
                "status": "not_initialized",
                "is_running": False,
                "guilds": 0,
                "users": 0,
                "latency": 0
            }
        
        return {
            "status": "online" if self.is_running and not self.bot.is_closed() else "offline",
            "is_running": self.is_running,
            "guilds": len(self.bot.guilds) if self.bot.guilds else 0,
            "users": len(self.bot.users) if self.bot.users else 0,
            "latency": round(self.bot.latency * 1000) if self.bot.latency else 0,
            "user": str(self.bot.user) if self.bot.user else None
        }
    
    async def send_message(self, channel_id: int, message: str) -> bool:
        """Send message to specific channel"""
        try:
            if not self.bot or not self.is_running:
                return False
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel {channel_id} not found")
                return False
            
            await channel.send(message)
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def _run_bot(self):
        """Run bot in background"""
        try:
            await self.bot.start(self.token)
        except Exception as e:
            logger.error(f"Bot run error: {e}")
            self.is_running = False
    
    async def _setup_commands(self):
        """Setup additional bot commands"""
        
        @self.bot.command(name="status")
        async def status_command(ctx):
            """Get bot status"""
            status = self.get_status()
            embed = discord.Embed(
                title="Bot Status",
                color=discord.Color.green() if status["is_running"] else discord.Color.red()
            )
            embed.add_field(name="Status", value=status["status"], inline=True)
            embed.add_field(name="Guilds", value=status["guilds"], inline=True)
            embed.add_field(name="Users", value=status["users"], inline=True)
            embed.add_field(name="Latency", value=f"{status['latency']}ms", inline=True)
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name="sync")
        @commands.has_permissions(administrator=True)
        async def sync_command(ctx):
            """Sync slash commands"""
            try:
                synced = await self.bot.tree.sync()
                await ctx.send(f"Synced {len(synced)} commands")
            except Exception as e:
                await ctx.send(f"Error syncing commands: {e}")


# Global bot service instance
bot_service = DiscordBotService()

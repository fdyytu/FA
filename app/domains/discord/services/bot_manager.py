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
        self.config_source = None  # "database" or "environment"
        
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
                logger.info("Discord bot manager initialized successfully from env")
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing bot manager from env: {e}")
            return False
    
    async def initialize_from_database(self, db_session=None) -> bool:
        """Initialize bot dari database configuration"""
        try:
            if not db_session:
                from app.core.database import SessionLocal
                db_session = SessionLocal()
                should_close = True
            else:
                should_close = False
            
            try:
                from app.domains.discord.services.discord_config_service import discord_config_service
                
                # Get active config from database
                active_config = discord_config_service.get_active_config(db_session)
                
                if not active_config:
                    logger.warning("Tidak ada konfigurasi Discord aktif di database")
                    return False
                
                # Decrypt token
                discord_token = discord_config_service.get_decrypted_token(active_config)
                
                if not discord_token:
                    logger.error("Token Discord tidak valid di database")
                    return False
                
                success = await self.bot_service.initialize(
                    token=discord_token,
                    command_prefix=active_config.command_prefix
                )
                
                if success:
                    self.is_initialized = True
                    self.config_source = "database"
                    logger.info(f"Discord bot manager initialized successfully from database: {active_config.name}")
                
                return success
                
            finally:
                if should_close:
                    db_session.close()
            
        except Exception as e:
            logger.error(f"Error initializing bot manager from database: {e}")
            return False
    
    async def auto_initialize(self, db_session=None) -> bool:
        """Auto initialize bot dari database atau environment variables"""
        try:
            # Try database first
            success = await self.initialize_from_database(db_session)
            if success:
                return True
            
            # Fallback to environment variables
            logger.info("Fallback ke environment variables untuk inisialisasi bot")
            success = await self.initialize_from_env()
            if success:
                self.config_source = "environment"
            
            return success
            
        except Exception as e:
            logger.error(f"Error auto initializing bot manager: {e}")
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
            if not self.bot_service:
                return {
                    "status": "not_initialized",
                    "is_running": False,
                    "manager_initialized": False,
                    "error": "Bot service not available",
                    "guilds": [],  # Tambahkan list guilds kosong
                    "guilds_count": 0,
                    "users_count": 0
                }
    
            base_status = self.bot_service.get_status()
            
            # Check token configuration from both sources
            env_token_configured = bool(os.getenv("DISCORD_TOKEN"))
            db_token_configured = False
            
            try:
                from app.core.database import SessionLocal
                from app.domains.discord.services.discord_config_service import discord_config_service
                
                db = SessionLocal()
                try:
                    active_config = discord_config_service.get_active_config(db)
                    db_token_configured = bool(active_config and active_config.token)
                finally:
                    db.close()
            except Exception:
                pass  # Ignore database errors for status check
            
            # Ambil informasi guild jika bot aktif
            guilds_info = []
            if self.bot_service.bot and self.bot_service.is_running:
                try:
                    guilds_info = [
                        {
                            "id": str(guild.id),  # Convert ke string untuk JSON
                            "name": guild.name,
                            "member_count": guild.member_count if hasattr(guild, 'member_count') else 0,
                            "icon": str(guild.icon.url) if guild.icon else None,
                            "owner_id": str(guild.owner_id) if hasattr(guild, 'owner_id') else None,
                            "permissions": True  # Asumsi bot punya akses
                        }
                        for guild in self.bot_service.bot.guilds
                    ]
                except Exception as guild_error:
                    logger.warning(f"Error getting guilds info: {guild_error}")
                    guilds_info = []
    
            # Hitung total users dari guilds
            total_users = sum(guild.get('member_count', 0) for guild in guilds_info)
                
            return {
                **base_status,
                "manager_initialized": self.is_initialized,
                "config_source": self.config_source,
                "token_configured": env_token_configured or db_token_configured,
                "token_sources": {
                    "environment": env_token_configured,
                    "database": db_token_configured
                },
                "environment": {
                    "command_prefix": os.getenv("DISCORD_COMMAND_PREFIX", "!"),
                    "guild_id": os.getenv("DISCORD_GUILD_ID"),
                },
                # Tambahkan informasi guild
                "guilds": guilds_info,
                "guilds_count": len(guilds_info),
                "users_count": total_users,
                # Status yang lebih detail
                "detailed_status": {
                    "uptime": self.bot_service.get_uptime() if hasattr(self.bot_service, 'get_uptime') else None,
                    "last_connect": self.bot_service.last_connect.isoformat() if (hasattr(self.bot_service, 'last_connect') and self.bot_service.last_connect is not None) else None,
                    "ready": self.bot_service.is_ready if hasattr(self.bot_service, 'is_ready') else False
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "manager_initialized": self.is_initialized,
                "config_source": self.config_source,
                "guilds": [],  # Tambahkan list guilds kosong
                "guilds_count": 0,
                "users_count": 0,
                "token_configured": False,
                "token_sources": {
                    "environment": False,
                    "database": False
                }
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

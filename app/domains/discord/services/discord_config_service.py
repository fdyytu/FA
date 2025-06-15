"""
Discord Configuration Service
Service untuk mengelola konfigurasi Discord Bot dengan enkripsi
"""
import os
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import base64
import hashlib

from app.domains.discord.models.discord_config import DiscordConfig
from app.domains.discord.repositories.discord_config_repository import discord_config_repository
from app.domains.discord.schemas.discord_config_schemas import (
    DiscordConfigCreate, DiscordConfigUpdate, DiscordConfigResponse
)

logger = logging.getLogger(__name__)


class DiscordConfigService:
    """Service untuk mengelola konfigurasi Discord"""
    
    def __init__(self):
        self._cipher = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption cipher"""
        try:
            secret_key = os.getenv("SECRET_KEY", "default-secret-key-for-development")
            # Create a Fernet key from the secret key
            key = base64.urlsafe_b64encode(
                hashlib.sha256(secret_key.encode()).digest()
            )
            self._cipher = Fernet(key)
        except Exception as e:
            logger.error(f"Error initializing encryption: {e}")
            self._cipher = None
    
    def _encrypt_token(self, token: str) -> str:
        """Encrypt Discord token"""
        try:
            if self._cipher and token:
                encrypted = self._cipher.encrypt(token.encode())
                return base64.urlsafe_b64encode(encrypted).decode()
            return token
        except Exception as e:
            logger.error(f"Error encrypting token: {e}")
            return token
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt Discord token"""
        try:
            if self._cipher and encrypted_token:
                decoded = base64.urlsafe_b64decode(encrypted_token.encode())
                decrypted = self._cipher.decrypt(decoded)
                return decrypted.decode()
            return encrypted_token
        except Exception as e:
            logger.error(f"Error decrypting token: {e}")
            return encrypted_token
    
    def create_config(self, db: Session, config_data: DiscordConfigCreate) -> DiscordConfig:
        """Buat konfigurasi Discord baru"""
        try:
            # Deactivate other configs if this is set as active
            if config_data.is_active:
                discord_config_repository.deactivate_all(db)
            
            # Encrypt token
            encrypted_token = self._encrypt_token(config_data.token)
            
            # Create new config
            config_dict = {
                "name": config_data.name,
                "token": encrypted_token,
                "guild_id": config_data.guild_id,
                "command_prefix": config_data.command_prefix,
                "is_active": config_data.is_active,
                "is_encrypted": bool(self._cipher)
            }
            
            db_config = discord_config_repository.create(db, config_dict)
            
            logger.info(f"Created Discord config: {db_config.name}")
            return db_config
            
        except Exception as e:
            logger.error(f"Error creating Discord config: {e}")
            db.rollback()
            raise
    
    def get_config(self, db: Session, config_id: int) -> Optional[DiscordConfig]:
        """Ambil konfigurasi berdasarkan ID"""
        return discord_config_repository.get_by_id(db, config_id)
    
    def get_active_config(self, db: Session) -> Optional[DiscordConfig]:
        """Ambil konfigurasi yang aktif"""
        return discord_config_repository.get_active_config(db)
    
    def get_all_configs(self, db: Session, skip: int = 0, limit: int = 100) -> List[DiscordConfig]:
        """Ambil semua konfigurasi"""
        return discord_config_repository.get_all(db, skip=skip, limit=limit)
    
    def update_config(self, db: Session, config_id: int, config_data: DiscordConfigUpdate) -> Optional[DiscordConfig]:
        """Update konfigurasi Discord"""
        try:
            db_config = self.get_config(db, config_id)
            if not db_config:
                return None
            
            # Update fields
            update_data = config_data.dict(exclude_unset=True)
            
            # Handle token encryption
            if 'token' in update_data and update_data['token']:
                update_data['token'] = self._encrypt_token(update_data['token'])
                update_data['is_encrypted'] = bool(self._cipher)
            
            # Handle active status
            if update_data.get('is_active', False):
                discord_config_repository.deactivate_all(db, exclude_id=config_id)
            
            db_config = discord_config_repository.update(db, config_id, update_data)
            
            logger.info(f"Updated Discord config: {db_config.name}")
            return db_config
            
        except Exception as e:
            logger.error(f"Error updating Discord config: {e}")
            db.rollback()
            raise
    
    def delete_config(self, db: Session, config_id: int) -> bool:
        """Hapus konfigurasi Discord"""
        try:
            db_config = self.get_config(db, config_id)
            if not db_config:
                return False
            
            success = discord_config_repository.delete(db, config_id)
            
            if success:
                logger.info(f"Deleted Discord config: {db_config.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting Discord config: {e}")
            db.rollback()
            raise
    
    def get_decrypted_token(self, config: DiscordConfig) -> str:
        """Ambil token yang sudah didekripsi"""
        if config.is_encrypted:
            return self._decrypt_token(config.token)
        return config.token
    

    
    async def test_token(self, token: str, guild_id: Optional[str] = None) -> dict:
        """Test validitas Discord token"""
        try:
            import discord
            from discord.ext import commands
            
            # Create temporary bot instance for testing
            intents = discord.Intents.default()
            intents.message_content = True
            
            bot = commands.Bot(command_prefix='!', intents=intents)
            
            @bot.event
            async def on_ready():
                result = {
                    'success': True,
                    'message': 'Token valid dan bot berhasil terhubung',
                    'bot_info': {
                        'name': bot.user.name,
                        'id': str(bot.user.id),
                        'discriminator': bot.user.discriminator,
                        'guilds_count': len(bot.guilds)
                    }
                }
                
                # Test guild access if guild_id provided
                if guild_id:
                    guild = bot.get_guild(int(guild_id))
                    if guild:
                        result['guild_info'] = {
                            'name': guild.name,
                            'id': str(guild.id),
                            'member_count': guild.member_count
                        }
                    else:
                        result['errors'] = [f'Bot tidak memiliki akses ke guild {guild_id}']
                
                await bot.close()
                return result
            
            # Start bot and wait for connection
            await bot.start(token)
            
        except discord.LoginFailure:
            return {
                'success': False,
                'message': 'Token tidak valid',
                'errors': ['Token Discord tidak valid atau sudah expired']
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error testing token: {str(e)}',
                'errors': [str(e)]
            }


# Global service instance
discord_config_service = DiscordConfigService()

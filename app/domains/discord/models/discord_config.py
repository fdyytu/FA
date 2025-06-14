"""
Discord Configuration Model
Model untuk menyimpan konfigurasi Discord Bot di database
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class DiscordConfig(Base):
    """Model untuk konfigurasi Discord Bot"""
    __tablename__ = "discord_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="Default Config")
    token = Column(Text, nullable=False)  # Encrypted token
    guild_id = Column(String(50), nullable=True)
    command_prefix = Column(String(10), nullable=False, default="!")
    is_active = Column(Boolean, default=True)
    is_encrypted = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DiscordConfig(id={self.id}, name='{self.name}', is_active={self.is_active})>"

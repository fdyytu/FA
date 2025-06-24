"""
Discord schemas - dipecah dari admin_schemas.py
Berisi schema untuk Discord configuration management
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DiscordConfigCreate(BaseModel):
    """Schema untuk membuat konfigurasi Discord baru"""
    name: str = Field(..., min_length=1, max_length=100, description="Nama konfigurasi")
    token: str = Field(..., min_length=50, description="Discord bot token")
    guild_id: Optional[str] = Field(None, description="Discord Guild ID")
    command_prefix: str = Field("!", max_length=10, description="Command prefix untuk bot")
    is_active: bool = Field(True, description="Status aktif konfigurasi")


class DiscordConfigUpdate(BaseModel):
    """Schema untuk update konfigurasi Discord"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    token: Optional[str] = Field(None, min_length=50)
    guild_id: Optional[str] = None
    command_prefix: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None


class DiscordConfigResponse(BaseModel):
    """Schema untuk response konfigurasi Discord"""
    id: int
    name: str
    token: str  # Will be masked in response
    guild_id: Optional[str]
    command_prefix: str
    is_active: bool
    is_encrypted: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

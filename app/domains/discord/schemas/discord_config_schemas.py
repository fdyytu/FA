"""
Discord Configuration Schemas
Pydantic schemas untuk validasi data konfigurasi Discord
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class DiscordConfigBase(BaseModel):
    """Base schema untuk Discord configuration"""
    name: str = Field(..., min_length=1, max_length=100, description="Nama konfigurasi")
    token: str = Field(..., min_length=50, description="Discord bot token")
    guild_id: Optional[str] = Field(None, description="Discord Guild ID")
    command_prefix: str = Field("!", max_length=10, description="Command prefix untuk bot")
    is_active: bool = Field(True, description="Status aktif konfigurasi")
    
    @validator('token')
    def validate_token(cls, v):
        """Validasi format Discord token"""
        if not v:
            raise ValueError('Token tidak boleh kosong')
        
        # Basic Discord token format validation
        # Discord tokens usually start with specific patterns
        if len(v) < 50:
            raise ValueError('Token terlalu pendek')
            
        return v
    
    @validator('guild_id')
    def validate_guild_id(cls, v):
        """Validasi Guild ID"""
        if v and not v.isdigit():
            raise ValueError('Guild ID harus berupa angka')
        return v
    
    @validator('command_prefix')
    def validate_command_prefix(cls, v):
        """Validasi command prefix"""
        if not v:
            raise ValueError('Command prefix tidak boleh kosong')
        
        # Tidak boleh mengandung spasi atau karakter khusus tertentu
        if ' ' in v or '\n' in v or '\t' in v:
            raise ValueError('Command prefix tidak boleh mengandung spasi atau karakter khusus')
            
        return v


class DiscordConfigCreate(DiscordConfigBase):
    """Schema untuk membuat konfigurasi Discord baru"""
    pass


class DiscordConfigUpdate(BaseModel):
    """Schema untuk update konfigurasi Discord"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    token: Optional[str] = Field(None, min_length=50)
    guild_id: Optional[str] = None
    command_prefix: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None
    
    @validator('token')
    def validate_token(cls, v):
        """Validasi format Discord token"""
        if v is not None:
            if len(v) < 50:
                raise ValueError('Token terlalu pendek')
        return v
    
    @validator('guild_id')
    def validate_guild_id(cls, v):
        """Validasi Guild ID"""
        if v is not None and v and not v.isdigit():
            raise ValueError('Guild ID harus berupa angka')
        return v


class DiscordConfigResponse(DiscordConfigBase):
    """Schema untuk response konfigurasi Discord"""
    id: int
    is_encrypted: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Mask token untuk keamanan
    @validator('token', pre=False, always=True)
    def mask_token(cls, v):
        """Mask token untuk response"""
        if v and len(v) > 10:
            return f"{v[:10]}...{v[-4:]}"
        return "***masked***"
    
    class Config:
        from_attributes = True


class DiscordConfigTest(BaseModel):
    """Schema untuk test konfigurasi Discord"""
    token: str = Field(..., min_length=50, description="Discord bot token untuk ditest")
    guild_id: Optional[str] = Field(None, description="Discord Guild ID untuk ditest")
    
    @validator('token')
    def validate_token(cls, v):
        """Validasi format Discord token"""
        if not v or len(v) < 50:
            raise ValueError('Token tidak valid')
        return v


class DiscordConfigTestResult(BaseModel):
    """Schema untuk hasil test konfigurasi"""
    success: bool
    message: str
    bot_info: Optional[dict] = None
    guild_info: Optional[dict] = None
    errors: Optional[list] = None

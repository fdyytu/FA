"""
Discord Admin Schemas
Schema untuk endpoint admin Discord
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class DiscordLogResponse(BaseModel):
    """Response schema untuk Discord Log"""
    id: int
    user_id: Optional[int] = None
    bot_id: Optional[int] = None
    level: str
    message: str
    action: Optional[str] = None
    channel_id: Optional[str] = None
    guild_id: Optional[str] = None
    error_details: Optional[str] = None
    extra_data: Optional[str] = None
    created_at: datetime
    
    # User info jika ada
    user_discord_username: Optional[str] = None
    user_discord_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class DiscordCommandResponse(BaseModel):
    """Response schema untuk Discord Command"""
    id: int
    user_id: Optional[int] = None
    command_name: str
    command_args: Optional[str] = None
    channel_id: str
    guild_id: str
    success: bool
    execution_time: Optional[Decimal] = None
    error_message: Optional[str] = None
    response_message: Optional[str] = None
    created_at: datetime
    
    # User info jika ada
    user_discord_username: Optional[str] = None
    user_discord_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class DiscordLogFilter(BaseModel):
    """Filter untuk Discord Logs"""
    level: Optional[str] = None
    action: Optional[str] = None
    bot_id: Optional[int] = None
    user_id: Optional[int] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class DiscordCommandFilter(BaseModel):
    """Filter untuk Discord Commands"""
    command_name: Optional[str] = None
    success: Optional[bool] = None
    user_id: Optional[int] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class DiscordStatsResponse(BaseModel):
    """Response schema untuk Discord Statistics"""
    total_logs: int
    logs_by_level: dict
    total_commands: int
    successful_commands: int
    failed_commands: int
    top_commands: List[dict]
    active_users: int
    total_bots: int
    active_bots: int


class PaginatedDiscordLogsResponse(BaseModel):
    """Response schema untuk paginated Discord logs"""
    items: List[DiscordLogResponse]
    total: int
    page: int
    size: int
    pages: int


class PaginatedDiscordCommandsResponse(BaseModel):
    """Response schema untuk paginated Discord commands"""
    items: List[DiscordCommandResponse]
    total: int
    page: int
    size: int
    pages: int

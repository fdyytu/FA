"""
Discord Admin Schemas
Schemas untuk Discord admin operations
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DiscordLogFilter(BaseModel):
    """Filter untuk Discord logs"""
    level: Optional[str] = None
    action: Optional[str] = None
    bot_id: Optional[int] = None
    user_id: Optional[int] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None


class DiscordCommandFilter(BaseModel):
    """Filter untuk Discord commands"""
    command_name: Optional[str] = None
    success: Optional[bool] = None
    user_id: Optional[int] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None


class DiscordLogResponse(BaseModel):
    """Response untuk Discord log"""
    id: int
    level: str
    action: str
    bot_id: int
    user_id: int
    guild_id: str
    channel_id: str
    message: str
    timestamp: str


class DiscordCommandResponse(BaseModel):
    """Response untuk Discord command"""
    id: int
    command_name: str
    user_id: int
    username: str
    guild_id: str
    channel_id: str
    success: bool
    response_time: int
    timestamp: str
    error_message: Optional[str] = None


class DiscordStatsResponse(BaseModel):
    """Response untuk Discord statistics"""
    success: bool
    data: Dict[str, Any]


class PaginatedDiscordLogsResponse(BaseModel):
    """Response untuk paginated Discord logs"""
    success: bool
    data: Dict[str, Any]


class PaginatedDiscordCommandsResponse(BaseModel):
    """Response untuk paginated Discord commands"""
    success: bool
    data: Dict[str, Any]

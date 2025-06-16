"""
Discord Admin Service
Service untuk mengelola operasi Discord admin
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domains.discord.repositories.discord_admin_repository import DiscordAdminRepository
from app.domains.discord.schemas.discord_admin_schemas import (
    DiscordLogResponse, DiscordCommandResponse, DiscordLogFilter, 
    DiscordCommandFilter, DiscordStatsResponse, PaginatedDiscordLogsResponse,
    PaginatedDiscordCommandsResponse
)
from app.domains.discord.models.discord import DiscordLog, DiscordCommand


class DiscordAdminService:
    """Service untuk Discord Admin operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = DiscordAdminRepository(db)
    
    def get_discord_logs(
        self, 
        page: int = 1, 
        size: int = 10,
        filters: Optional[DiscordLogFilter] = None
    ) -> PaginatedDiscordLogsResponse:
        """Ambil Discord logs dengan pagination"""
        skip = (page - 1) * size
        logs, total = self.repository.get_discord_logs(skip, size, filters)
        
        # Convert to response format
        log_responses = []
        for log in logs:
            log_response = DiscordLogResponse(
                id=log.id,
                user_id=log.user_id,
                bot_id=log.bot_id,
                level=log.level,
                message=log.message,
                action=log.action,
                channel_id=log.channel_id,
                guild_id=log.guild_id,
                error_details=log.error_details,
                extra_data=log.extra_data,
                created_at=log.created_at,
                user_discord_username=log.user.discord_username if log.user else None,
                user_discord_id=log.user.discord_id if log.user else None
            )
            log_responses.append(log_response)
        
        pages = (total + size - 1) // size
        
        return PaginatedDiscordLogsResponse(
            items=log_responses,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def get_discord_commands(
        self, 
        page: int = 1, 
        size: int = 5,
        filters: Optional[DiscordCommandFilter] = None
    ) -> PaginatedDiscordCommandsResponse:
        """Ambil Discord commands dengan pagination"""
        skip = (page - 1) * size
        commands, total = self.repository.get_discord_commands(skip, size, filters)
        
        # Convert to response format
        command_responses = []
        for command in commands:
            command_response = DiscordCommandResponse(
                id=command.id,
                user_id=command.user_id,
                command_name=command.command_name,
                command_args=command.command_args,
                channel_id=command.channel_id,
                guild_id=command.guild_id,
                success=command.success,
                execution_time=command.execution_time,
                error_message=command.error_message,
                response_message=command.response_message,
                created_at=command.created_at,
                user_discord_username=command.user.discord_username if command.user else None,
                user_discord_id=command.user.discord_id if command.user else None
            )
            command_responses.append(command_response)
        
        pages = (total + size - 1) // size
        
        return PaginatedDiscordCommandsResponse(
            items=command_responses,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def get_recent_discord_commands(self, limit: int = 5) -> List[DiscordCommandResponse]:
        """Ambil recent Discord commands"""
        commands = self.repository.get_recent_discord_commands(limit)
        
        command_responses = []
        for command in commands:
            command_response = DiscordCommandResponse(
                id=command.id,
                user_id=command.user_id,
                command_name=command.command_name,
                command_args=command.command_args,
                channel_id=command.channel_id,
                guild_id=command.guild_id,
                success=command.success,
                execution_time=command.execution_time,
                error_message=command.error_message,
                response_message=command.response_message,
                created_at=command.created_at,
                user_discord_username=command.user.discord_username if command.user else None,
                user_discord_id=command.user.discord_id if command.user else None
            )
            command_responses.append(command_response)
        
        return command_responses
    
    def get_discord_stats(self) -> DiscordStatsResponse:
        """Ambil statistik Discord"""
        stats = self.repository.get_discord_stats()
        
        return DiscordStatsResponse(
            total_logs=stats["total_logs"],
            logs_by_level=stats["logs_by_level"],
            total_commands=stats["total_commands"],
            successful_commands=stats["successful_commands"],
            failed_commands=stats["failed_commands"],
            top_commands=stats["top_commands"],
            active_users=stats["active_users"],
            total_bots=stats["total_bots"],
            active_bots=stats["active_bots"]
        )
    
    def create_discord_log(
        self,
        level: str,
        message: str,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
        bot_id: Optional[int] = None,
        channel_id: Optional[str] = None,
        guild_id: Optional[str] = None,
        error_details: Optional[str] = None,
        extra_data: Optional[str] = None
    ) -> DiscordLogResponse:
        """Buat log Discord baru"""
        log = self.repository.create_discord_log(
            level=level,
            message=message,
            action=action,
            user_id=user_id,
            bot_id=bot_id,
            channel_id=channel_id,
            guild_id=guild_id,
            error_details=error_details,
            extra_data=extra_data
        )
        
        return DiscordLogResponse(
            id=log.id,
            user_id=log.user_id,
            bot_id=log.bot_id,
            level=log.level,
            message=log.message,
            action=log.action,
            channel_id=log.channel_id,
            guild_id=log.guild_id,
            error_details=log.error_details,
            extra_data=log.extra_data,
            created_at=log.created_at
        )
    
    def create_discord_command(
        self,
        command_name: str,
        channel_id: str,
        guild_id: str,
        user_id: Optional[int] = None,
        command_args: Optional[str] = None,
        success: bool = True,
        execution_time: Optional[float] = None,
        error_message: Optional[str] = None,
        response_message: Optional[str] = None
    ) -> DiscordCommandResponse:
        """Buat record command Discord baru"""
        command = self.repository.create_discord_command(
            command_name=command_name,
            channel_id=channel_id,
            guild_id=guild_id,
            user_id=user_id,
            command_args=command_args,
            success=success,
            execution_time=execution_time,
            error_message=error_message,
            response_message=response_message
        )
        
        return DiscordCommandResponse(
            id=command.id,
            user_id=command.user_id,
            command_name=command.command_name,
            command_args=command.command_args,
            channel_id=command.channel_id,
            guild_id=command.guild_id,
            success=command.success,
            execution_time=command.execution_time,
            error_message=command.error_message,
            response_message=command.response_message,
            created_at=command.created_at
        )

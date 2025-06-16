"""
Discord Admin Repository
Repository untuk mengelola data Discord logs dan commands
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from app.domains.discord.models.discord import DiscordLog, DiscordCommand, DiscordUser, DiscordBot
from app.domains.discord.schemas.discord_admin_schemas import DiscordLogFilter, DiscordCommandFilter


class DiscordAdminRepository:
    """Repository untuk Discord Admin operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_discord_logs(
        self, 
        skip: int = 0, 
        limit: int = 10,
        filters: Optional[DiscordLogFilter] = None
    ) -> Tuple[List[DiscordLog], int]:
        """Ambil Discord logs dengan filter dan pagination"""
        query = self.db.query(DiscordLog).options(
            joinedload(DiscordLog.user)
        )
        
        # Apply filters
        if filters:
            if filters.level:
                query = query.filter(DiscordLog.level == filters.level)
            if filters.action:
                query = query.filter(DiscordLog.action == filters.action)
            if filters.bot_id:
                query = query.filter(DiscordLog.bot_id == filters.bot_id)
            if filters.user_id:
                query = query.filter(DiscordLog.user_id == filters.user_id)
            if filters.guild_id:
                query = query.filter(DiscordLog.guild_id == filters.guild_id)
            if filters.channel_id:
                query = query.filter(DiscordLog.channel_id == filters.channel_id)
            if filters.start_date:
                query = query.filter(DiscordLog.created_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(DiscordLog.created_at <= filters.end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(desc(DiscordLog.created_at)).offset(skip).limit(limit).all()
        
        return logs, total
    
    def get_discord_commands(
        self, 
        skip: int = 0, 
        limit: int = 5,
        filters: Optional[DiscordCommandFilter] = None
    ) -> Tuple[List[DiscordCommand], int]:
        """Ambil Discord commands dengan filter dan pagination"""
        query = self.db.query(DiscordCommand).options(
            joinedload(DiscordCommand.user)
        )
        
        # Apply filters
        if filters:
            if filters.command_name:
                query = query.filter(DiscordCommand.command_name.ilike(f"%{filters.command_name}%"))
            if filters.success is not None:
                query = query.filter(DiscordCommand.success == filters.success)
            if filters.user_id:
                query = query.filter(DiscordCommand.user_id == filters.user_id)
            if filters.guild_id:
                query = query.filter(DiscordCommand.guild_id == filters.guild_id)
            if filters.channel_id:
                query = query.filter(DiscordCommand.channel_id == filters.channel_id)
            if filters.start_date:
                query = query.filter(DiscordCommand.created_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(DiscordCommand.created_at <= filters.end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        commands = query.order_by(desc(DiscordCommand.created_at)).offset(skip).limit(limit).all()
        
        return commands, total
    
    def get_recent_discord_commands(self, limit: int = 5) -> List[DiscordCommand]:
        """Ambil recent Discord commands"""
        return self.db.query(DiscordCommand).options(
            joinedload(DiscordCommand.user)
        ).order_by(desc(DiscordCommand.created_at)).limit(limit).all()
    
    def get_discord_stats(self) -> Dict[str, Any]:
        """Ambil statistik Discord"""
        # Total logs
        total_logs = self.db.query(DiscordLog).count()
        
        # Logs by level
        logs_by_level = dict(
            self.db.query(DiscordLog.level, func.count(DiscordLog.id))
            .group_by(DiscordLog.level)
            .all()
        )
        
        # Total commands
        total_commands = self.db.query(DiscordCommand).count()
        successful_commands = self.db.query(DiscordCommand).filter(DiscordCommand.success == True).count()
        failed_commands = total_commands - successful_commands
        
        # Top commands
        top_commands = (
            self.db.query(
                DiscordCommand.command_name,
                func.count(DiscordCommand.id).label('count')
            )
            .group_by(DiscordCommand.command_name)
            .order_by(desc('count'))
            .limit(10)
            .all()
        )
        
        top_commands_list = [
            {"command": cmd[0], "count": cmd[1]} 
            for cmd in top_commands
        ]
        
        # Active users (users who executed commands in last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        active_users = (
            self.db.query(DiscordCommand.user_id)
            .filter(DiscordCommand.created_at >= yesterday)
            .distinct()
            .count()
        )
        
        # Bot stats
        total_bots = self.db.query(DiscordBot).count()
        active_bots = self.db.query(DiscordBot).filter(DiscordBot.is_active == True).count()
        
        return {
            "total_logs": total_logs,
            "logs_by_level": logs_by_level,
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "failed_commands": failed_commands,
            "top_commands": top_commands_list,
            "active_users": active_users,
            "total_bots": total_bots,
            "active_bots": active_bots
        }
    
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
    ) -> DiscordLog:
        """Buat log Discord baru"""
        log = DiscordLog(
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
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
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
    ) -> DiscordCommand:
        """Buat record command Discord baru"""
        command = DiscordCommand(
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
        
        self.db.add(command)
        self.db.commit()
        self.db.refresh(command)
        
        return command

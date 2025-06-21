import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from app.domains.discord.repositories.command_log_repository import CommandLogRepository
from app.core.database import get_db

class CommandTracker:
    def __init__(self):
        self.active_commands = {}
    
    async def start_tracking(self, command_id: str, user_data: Dict[str, Any], 
                           command: str, args: Optional[str] = None) -> None:
        """Mulai tracking command"""
        self.active_commands[command_id] = {
            "start_time": time.time(),
            "user_data": user_data,
            "command": command,
            "args": args
        }
    
    async def end_tracking(self, command_id: str, success: bool = True, 
                         response: Optional[str] = None, 
                         error: Optional[str] = None) -> None:
        """Selesai tracking dan simpan ke database"""
        if command_id not in self.active_commands:
            return
        
        tracking_data = self.active_commands.pop(command_id)
        execution_time = int((time.time() - tracking_data["start_time"]) * 1000)
        
        log_data = {
            "user_id": tracking_data["user_data"].get("user_id"),
            "username": tracking_data["user_data"].get("username"),
            "channel_id": tracking_data["user_data"].get("channel_id"),
            "channel_name": tracking_data["user_data"].get("channel_name"),
            "guild_id": tracking_data["user_data"].get("guild_id"),
            "guild_name": tracking_data["user_data"].get("guild_name"),
            "command": tracking_data["command"],
            "command_args": tracking_data["args"],
            "response_status": "success" if success else "error",
            "response_message": response,
            "execution_time_ms": execution_time,
            "error_message": error,
            "is_successful": success,
            "timestamp": datetime.utcnow()
        }
        
        # Simpan ke database
        db = next(get_db())
        try:
            repo = CommandLogRepository(db)
            repo.create_log(log_data)
        finally:
            db.close()
    
    def get_active_commands_count(self) -> int:
        """Jumlah command yang sedang berjalan"""
        return len(self.active_commands)
    
    def cleanup_stale_commands(self, max_age_seconds: int = 300) -> int:
        """Bersihkan command yang terlalu lama"""
        current_time = time.time()
        stale_commands = [
            cmd_id for cmd_id, data in self.active_commands.items()
            if current_time - data["start_time"] > max_age_seconds
        ]
        
        for cmd_id in stale_commands:
            self.active_commands.pop(cmd_id, None)
        
        return len(stale_commands)

# Global instance
command_tracker = CommandTracker()

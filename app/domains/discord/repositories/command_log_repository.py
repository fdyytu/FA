from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.domains.discord.models.command_log import DiscordCommandLog
from app.common.base_classes.base_repository import BaseRepository

class CommandLogRepository(BaseRepository[DiscordCommandLog]):
    def __init__(self, db: Session):
        super().__init__(db, DiscordCommandLog)
    
    def create_log(self, log_data: Dict[str, Any]) -> DiscordCommandLog:
        """Buat log command baru"""
        log = DiscordCommandLog(**log_data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_recent_logs(self, limit: int = 100) -> List[DiscordCommandLog]:
        """Ambil log terbaru"""
        return self.db.query(DiscordCommandLog)\
            .order_by(desc(DiscordCommandLog.timestamp))\
            .limit(limit).all()
    
    def get_logs_by_user(self, user_id: str, limit: int = 50) -> List[DiscordCommandLog]:
        """Ambil log berdasarkan user"""
        return self.db.query(DiscordCommandLog)\
            .filter(DiscordCommandLog.user_id == user_id)\
            .order_by(desc(DiscordCommandLog.timestamp))\
            .limit(limit).all()
    
    def get_failed_logs(self, hours: int = 24) -> List[DiscordCommandLog]:
        """Ambil log yang gagal dalam X jam terakhir"""
        since = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(DiscordCommandLog)\
            .filter(and_(
                DiscordCommandLog.is_successful == False,
                DiscordCommandLog.timestamp >= since
            )).order_by(desc(DiscordCommandLog.timestamp)).all()
    
    def get_command_stats(self, hours: int = 24) -> Dict[str, int]:
        """Statistik command dalam X jam terakhir"""
        since = datetime.utcnow() - timedelta(hours=hours)
        logs = self.db.query(DiscordCommandLog)\
            .filter(DiscordCommandLog.timestamp >= since).all()
        
        stats = {"total": len(logs), "success": 0, "failed": 0}
        for log in logs:
            if log.is_successful:
                stats["success"] += 1
            else:
                stats["failed"] += 1
        return stats

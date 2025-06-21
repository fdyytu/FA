import psutil
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.domains.discord.repositories.command_log_repository import CommandLogRepository
from app.core.database import get_db

class BotMonitor:
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.last_health_check = None
        self.performance_metrics = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "avg_response_time": 0.0
        }
    
    def get_uptime(self) -> Dict[str, Any]:
        """Hitung uptime bot"""
        uptime_delta = datetime.utcnow() - self.start_time
        return {
            "uptime_seconds": int(uptime_delta.total_seconds()),
            "uptime_formatted": str(uptime_delta).split('.')[0],
            "start_time": self.start_time.isoformat()
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Ambil metrics sistem"""
        process = psutil.Process()
        return {
            "memory_usage_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": round(process.cpu_percent(), 2),
            "threads_count": process.num_threads(),
            "system_memory_percent": round(psutil.virtual_memory().percent, 2),
            "system_cpu_percent": round(psutil.cpu_percent(), 2)
        }
    
    async def get_command_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Ambil metrics command dari database"""
        db = next(get_db())
        try:
            repo = CommandLogRepository(db)
            stats = repo.get_command_stats(hours)
            
            # Hitung average response time
            since = datetime.utcnow() - timedelta(hours=hours)
            recent_logs = repo.get_recent_logs(1000)
            
            if recent_logs:
                avg_time = sum(log.execution_time_ms for log in recent_logs) / len(recent_logs)
                stats["avg_response_time_ms"] = round(avg_time, 2)
            else:
                stats["avg_response_time_ms"] = 0.0
            
            return stats
        finally:
            db.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        self.last_health_check = datetime.utcnow()
        
        uptime = self.get_uptime()
        system = self.get_system_metrics()
        commands = await self.get_command_metrics()
        
        # Tentukan status kesehatan
        is_healthy = (
            system["memory_usage_mb"] < 512 and
            system["cpu_percent"] < 80 and
            uptime["uptime_seconds"] > 60
        )
        
        return {
            "healthy": is_healthy,
            "timestamp": self.last_health_check.isoformat(),
            "uptime": uptime,
            "system": system,
            "commands": commands,
            "status": "healthy" if is_healthy else "warning"
        }

# Global instance
bot_monitor = BotMonitor()

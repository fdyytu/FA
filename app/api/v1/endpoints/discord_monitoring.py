from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.core.database import get_db
from app.domains.discord.repositories.command_log_repository import CommandLogRepository
from app.domains.discord.services.bot_monitor import bot_monitor
from app.domains.discord.services.command_tracker import command_tracker

router = APIRouter()

@router.get("/monitoring/health")
async def get_bot_health() -> Dict[str, Any]:
    """Comprehensive bot health check"""
    try:
        health_data = await bot_monitor.health_check()
        return {
            "success": True,
            "data": health_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/metrics")
async def get_bot_metrics() -> Dict[str, Any]:
    """Get bot performance metrics"""
    try:
        uptime = bot_monitor.get_uptime()
        system = bot_monitor.get_system_metrics()
        commands = await bot_monitor.get_command_metrics()
        
        return {
            "success": True,
            "data": {
                "uptime": uptime,
                "system": system,
                "commands": commands,
                "active_commands": command_tracker.get_active_commands_count()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get recent command logs"""
    try:
        repo = CommandLogRepository(db)
        logs = repo.get_recent_logs(limit)
        
        return {
            "success": True,
            "data": {
                "logs": [log.to_dict() for log in logs],
                "total": len(logs)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/user/{user_id}")
async def get_user_logs(
    user_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get logs for specific user"""
    try:
        repo = CommandLogRepository(db)
        logs = repo.get_logs_by_user(user_id, limit)
        
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "logs": [log.to_dict() for log in logs],
                "total": len(logs)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/logs")
async def get_monitoring_logs(
    limit: int = Query(10, ge=1, le=100),
    level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get monitoring logs for dashboard"""
    try:
        # Mock response for now - in real implementation, this would query actual logs
        logs = [
            {
                "id": f"log_{i}",
                "timestamp": "2025-01-16T10:00:00Z",
                "level": "INFO" if i % 3 == 0 else ("WARNING" if i % 3 == 1 else "ERROR"),
                "message": f"Discord bot log message {i}",
                "bot_id": f"bot_{i % 3 + 1}",
                "guild_id": f"guild_{i % 2 + 1}",
                "user_id": f"user_{i}" if i % 2 == 0 else None
            }
            for i in range(1, limit + 1)
        ]
        
        # Apply level filter if provided
        if level:
            logs = [log for log in logs if log["level"] == level.upper()]
        
        return {
            "success": True,
            "data": {
                "logs": logs,
                "total": len(logs),
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/commands/recent")
async def get_recent_commands_monitoring(
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get recent commands for monitoring dashboard"""
    try:
        # Mock response for now - in real implementation, this would query actual command logs
        commands = [
            {
                "id": f"cmd_{i}",
                "command_name": f"command_{i}",
                "user_id": f"user_{i}",
                "guild_id": f"guild_{i % 2 + 1}",
                "channel_id": f"channel_{i}",
                "success": i % 3 != 0,
                "execution_time": f"{100 + i * 10}ms",
                "timestamp": "2025-01-16T10:00:00Z",
                "error_message": f"Error in command {i}" if i % 3 == 0 else None
            }
            for i in range(1, limit + 1)
        ]
        
        return {
            "success": True,
            "data": {
                "commands": commands,
                "total": len(commands),
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        # Get real logs from database
        repo = CommandLogRepository(db)
        logs = repo.get_recent_logs(limit)
        
        # Convert to dict format and apply level filter if provided
        log_data = []
        for log in logs:
            log_dict = log.to_dict()
            if level is None or log_dict.get("level", "").upper() == level.upper():
                log_data.append(log_dict)
        
        return {
            "success": True,
            "data": {
                "logs": log_data,
                "total": len(log_data),
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
        # Get real command logs from database
        repo = CommandLogRepository(db)
        logs = repo.get_recent_logs(limit)
        
        # Convert to command format
        commands = []
        for log in logs:
            log_dict = log.to_dict()
            command_data = {
                "id": log_dict.get("id"),
                "command_name": log_dict.get("command_name", "unknown"),
                "user_id": log_dict.get("user_id"),
                "guild_id": log_dict.get("guild_id"),
                "channel_id": log_dict.get("channel_id"),
                "success": log_dict.get("success", True),
                "execution_time": f"{log_dict.get('execution_time', 0)}ms",
                "timestamp": log_dict.get("timestamp"),
                "error_message": log_dict.get("error_message")
            }
            commands.append(command_data)
        
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

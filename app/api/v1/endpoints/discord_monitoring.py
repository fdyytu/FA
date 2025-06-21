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

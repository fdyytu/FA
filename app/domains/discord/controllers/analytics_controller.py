from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db

# Try to import Discord models
try:
    from app.models.discord import (
        DiscordBot, DiscordUser, LiveStock, AdminWorldConfig, DiscordBotStatus
    )
except ImportError:
    DiscordBot = DiscordUser = LiveStock = AdminWorldConfig = DiscordBotStatus = None

# Try to import utility functions
try:
    from app.utils.responses import create_success_response, create_error_response
except ImportError:
    def create_success_response(data, message="Success"):
        return {"success": True, "data": data, "message": message}
    def create_error_response(message, status_code=400):
        return {"success": False, "message": message, "status_code": status_code}

logger = logging.getLogger(__name__)


class DiscordAnalyticsController:
    """
    Controller untuk analytics Discord - Single Responsibility: Discord analytics, logs, and statistics endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk analytics Discord"""
        
        @self.router.get("/logs", response_model=dict)
        async def get_discord_logs(
            limit: int = 10,
            level: Optional[str] = None,
            db: Session = Depends(get_db)
        ):
            """Ambil log Discord Bot"""
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
                
                return create_success_response(
                    data={
                        "logs": logs,
                        "total": len(logs),
                        "limit": limit
                    }
                )
                
            except Exception as e:
                logger.error(f"Error getting Discord logs: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/commands/recent", response_model=dict)
        async def get_recent_commands(
            limit: int = 5,
            db: Session = Depends(get_db)
        ):
            """Ambil recent commands Discord Bot"""
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
                
                return create_success_response(
                    data={
                        "commands": commands,
                        "total": len(commands),
                        "limit": limit
                    }
                )
                
            except Exception as e:
                logger.error(f"Error getting recent commands: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/commands", response_model=dict)
        async def get_discord_commands(
            page: int = 1,
            limit: int = 10,
            command_name: Optional[str] = None,
            success: Optional[bool] = None,
            user_id: Optional[str] = None,
            guild_id: Optional[str] = None,
            channel_id: Optional[str] = None,
            db: Session = Depends(get_db)
        ):
            """Ambil Discord commands dengan filter"""
            try:
                # Mock response for now
                total = 100
                skip = (page - 1) * limit
                
                commands = [
                    {
                        "id": f"cmd_{skip + i}",
                        "command_name": f"command_{(skip + i) % 5 + 1}",
                        "user_id": f"user_{skip + i}",
                        "guild_id": f"guild_{(skip + i) % 3 + 1}",
                        "channel_id": f"channel_{skip + i}",
                        "success": (skip + i) % 4 != 0,
                        "execution_time": f"{100 + (skip + i) * 10}ms",
                        "timestamp": "2025-01-16T10:00:00Z",
                        "error_message": f"Error in command {skip + i}" if (skip + i) % 4 == 0 else None
                    }
                    for i in range(1, limit + 1)
                ]
                
                # Apply filters
                if command_name:
                    commands = [cmd for cmd in commands if command_name.lower() in cmd["command_name"].lower()]
                if success is not None:
                    commands = [cmd for cmd in commands if cmd["success"] == success]
                if user_id:
                    commands = [cmd for cmd in commands if cmd["user_id"] == user_id]
                if guild_id:
                    commands = [cmd for cmd in commands if cmd["guild_id"] == guild_id]
                if channel_id:
                    commands = [cmd for cmd in commands if cmd["channel_id"] == channel_id]
                
                return create_success_response(
                    data={
                        "commands": commands,
                        "total": total,
                        "page": page,
                        "limit": limit,
                        "pages": (total + limit - 1) // limit
                    }
                )
                
            except Exception as e:
                logger.error(f"Error getting Discord commands: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/stats", response_model=dict)
        async def get_discord_stats(
            db: Session = Depends(get_db)
        ):
            """Ambil statistik Discord Bot"""
            try:
                if not all([DiscordBot, DiscordUser, LiveStock, AdminWorldConfig]):
                    return create_success_response(
                        data={
                            "bots": {"total": 0, "active": 0, "inactive": 0},
                            "users": {"total": 0, "verified": 0, "unverified": 0},
                            "products": {"total": 0, "active": 0, "inactive": 0},
                            "worlds": {"total": 0, "active": 0, "inactive": 0}
                        }
                    )

                # Get bot stats
                total_bots = db.query(DiscordBot).count() if DiscordBot else 0
                active_bots = db.query(DiscordBot).filter(
                    DiscordBot.status == DiscordBotStatus.ACTIVE
                ).count() if DiscordBot and DiscordBotStatus else 0
                
                # Get user stats
                total_users = db.query(DiscordUser).count() if DiscordUser else 0
                verified_users = db.query(DiscordUser).filter(
                    DiscordUser.is_verified == True
                ).count() if DiscordUser else 0
                
                # Get product stats
                total_products = db.query(LiveStock).count() if LiveStock else 0
                active_products = db.query(LiveStock).filter(
                    LiveStock.is_active == True
                ).count() if LiveStock else 0
                
                # Get world stats
                total_worlds = db.query(AdminWorldConfig).count() if AdminWorldConfig else 0
                active_worlds = db.query(AdminWorldConfig).filter(
                    AdminWorldConfig.is_active == True
                ).count() if AdminWorldConfig else 0
                
                return create_success_response(
                    data={
                        "bots": {
                            "total": total_bots,
                            "active": active_bots,
                            "inactive": total_bots - active_bots
                        },
                        "users": {
                            "total": total_users,
                            "verified": verified_users,
                            "unverified": total_users - verified_users
                        },
                        "products": {
                            "total": total_products,
                            "active": active_products,
                            "inactive": total_products - active_products
                        },
                        "worlds": {
                            "total": total_worlds,
                            "active": active_worlds,
                            "inactive": total_worlds - active_worlds
                        }
                    }
                )
                
            except Exception as e:
                logger.error(f"Error getting Discord stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/stats/commands")
        async def get_command_stats(
            period: str = "daily",
            db: Session = Depends(get_db)
        ):
            """Ambil statistik command Discord"""
            try:
                # Mock data for command statistics
                if period == "daily":
                    stats = {
                        "total_commands": 1250,
                        "successful_commands": 1100,
                        "failed_commands": 150,
                        "success_rate": 88.0,
                        "most_used_commands": [
                            {"command": "help", "count": 300},
                            {"command": "balance", "count": 250},
                            {"command": "buy", "count": 200},
                            {"command": "sell", "count": 150},
                            {"command": "info", "count": 100}
                        ],
                        "hourly_distribution": [
                            {"hour": i, "count": 50 + (i * 5)} for i in range(24)
                        ]
                    }
                elif period == "weekly":
                    stats = {
                        "total_commands": 8750,
                        "successful_commands": 7700,
                        "failed_commands": 1050,
                        "success_rate": 88.0,
                        "daily_distribution": [
                            {"day": f"Day {i}", "count": 1000 + (i * 100)} for i in range(1, 8)
                        ]
                    }
                else:  # monthly
                    stats = {
                        "total_commands": 37500,
                        "successful_commands": 33000,
                        "failed_commands": 4500,
                        "success_rate": 88.0,
                        "weekly_distribution": [
                            {"week": f"Week {i}", "count": 8000 + (i * 500)} for i in range(1, 5)
                        ]
                    }
                
                return create_success_response(data=stats)
                
            except Exception as e:
                logger.error(f"Error getting command stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/stats/performance")
        async def get_performance_stats(
            db: Session = Depends(get_db)
        ):
            """Ambil statistik performa Discord Bot"""
            try:
                # Mock data for performance statistics
                stats = {
                    "uptime": "99.5%",
                    "average_response_time": "120ms",
                    "memory_usage": "256MB",
                    "cpu_usage": "15%",
                    "active_connections": 45,
                    "commands_per_minute": 25,
                    "error_rate": "2.1%",
                    "last_restart": "2025-01-15T08:30:00Z"
                }
                
                return create_success_response(data=stats)
                
            except Exception as e:
                logger.error(f"Error getting performance stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))


# Initialize controller
analytics_controller = DiscordAnalyticsController()

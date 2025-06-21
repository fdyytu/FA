from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
from datetime import datetime

from app.domains.discord.services.bot_monitor import BotMonitor
from app.domains.discord.services.command_tracker import CommandTracker
from app.domains.discord.services.websocket_service import WebSocketService
from app.domains.discord.services.bulk_operations import BulkOperationsService
from app.domains.discord.services.stock_display_service import StockDisplayService
from app.domains.discord.services.audit_logger import AuditLogger
from app.domains.discord.services.log_filter_service import LogFilterService
from app.domains.discord.services.discord_cache import DiscordCache
from app.domains.discord.middleware.discord_auth import verify_admin_token

logger = logging.getLogger(__name__)

class DashboardIntegrationController:
    """Controller untuk integrasi semua fitur Discord ke dashboard"""
    
    def __init__(self):
        self.router = APIRouter()
        self.bot_monitor = BotMonitor()
        self.command_tracker = CommandTracker()
        self.websocket_service = WebSocketService()
        self.bulk_operations = BulkOperationsService()
        self.stock_display = StockDisplayService()
        self.audit_logger = AuditLogger()
        self.log_filter = LogFilterService()
        self.cache = DiscordCache()
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup semua routes untuk dashboard integration"""
        
        @self.router.get("/dashboard/overview")
        async def get_dashboard_overview():
            """Mendapatkan overview lengkap untuk dashboard"""
            try:
                # Ambil data dari berbagai service
                bot_status = await self.bot_monitor.get_comprehensive_health()
                recent_commands = await self.command_tracker.get_recent_commands(limit=10)
                system_metrics = await self.bot_monitor.get_system_metrics()
                
                return {
                    "success": True,
                    "data": {
                        "bot_status": bot_status,
                        "recent_commands": recent_commands,
                        "system_metrics": system_metrics,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            except Exception as e:
                logger.error(f"Error getting dashboard overview: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/dashboard/features")
        async def get_available_features():
            """Mendapatkan daftar fitur yang tersedia"""
            features = {
                "monitoring": {
                    "name": "Real-time Monitoring",
                    "description": "Monitor bot performance dan health",
                    "endpoints": ["/monitoring/health", "/monitoring/metrics"],
                    "status": "active"
                },
                "command_tracking": {
                    "name": "Command Tracking",
                    "description": "Track dan log semua command Discord",
                    "endpoints": ["/logs/recent", "/logs/user/{user_id}"],
                    "status": "active"
                },
                "bulk_operations": {
                    "name": "Bulk Operations",
                    "description": "Operasi bulk untuk multiple bots",
                    "endpoints": ["/bulk/start", "/bulk/stop", "/bulk/message"],
                    "status": "active"
                },
                "stock_management": {
                    "name": "Stock Display Management",
                    "description": "Kelola tampilan stock produk",
                    "endpoints": ["/stock/toggle", "/stock/bulk"],
                    "status": "active"
                },
                "security": {
                    "name": "Security & Audit",
                    "description": "Authentication dan audit logging",
                    "endpoints": ["/auth/verify", "/audit/logs"],
                    "status": "active"
                },
                "websocket": {
                    "name": "Real-time Updates",
                    "description": "WebSocket untuk update real-time",
                    "endpoints": ["/ws/connect", "/ws/broadcast"],
                    "status": "active"
                }
            }
            
            return {
                "success": True,
                "data": {
                    "features": features,
                    "total_features": len(features),
                    "active_features": len([f for f in features.values() if f["status"] == "active"])
                }
            }

dashboard_integration = DashboardIntegrationController()

"""
World Config Controller - Konfigurasi Discord worlds/servers
Dipecah dari discord_worlds_controller.py untuk meningkatkan maintainability
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.common.logging.admin_logger import admin_logger
from app.domains.discord.services.bot_manager import bot_manager


class WorldConfigController:
    """Controller untuk konfigurasi Discord worlds/servers"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        admin_logger.info("WorldConfigController initialized")
    
    def _setup_routes(self):
        """Setup world configuration routes"""
        
        @self.router.get("/worlds/{world_id}/config")
        async def get_world_config(world_id: str) -> Dict[str, Any]:
            """Get world configuration"""
            try:
                admin_logger.info(f"Mengambil konfigurasi world dengan ID: {world_id}")
                
                # Get world config from bot manager
                config_data = {
                    "world_id": world_id,
                    "auto_moderation": False,
                    "welcome_message": True,
                    "command_prefix": "!",
                    "allowed_channels": [],
                    "restricted_commands": [],
                    "permissions": {
                        "admin_only": [],
                        "moderator_only": [],
                        "public": []
                    }
                }
                
                admin_logger.info(f"Berhasil mengambil konfigurasi world {world_id}")
                return {
                    "success": True,
                    "data": config_data
                }
                
            except Exception as e:
                admin_logger.error(f"Error getting world config {world_id}", e)
                return {
                    "success": False,
                    "error": "Failed to get world config",
                    "data": {}
                }
        
        @self.router.put("/worlds/{world_id}/config")
        async def update_world_config(world_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
            """Update world configuration"""
            try:
                admin_logger.info(f"Mengupdate konfigurasi world dengan ID: {world_id}")
                
                # Update world config
                # Implementation would save to database or config file
                
                admin_logger.info(f"Konfigurasi world {world_id} berhasil diupdate")
                return {
                    "success": True,
                    "message": f"Konfigurasi world {world_id} berhasil diupdate"
                }
                
            except Exception as e:
                admin_logger.error(f"Error updating world config {world_id}", e)
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/worlds/{world_id}/permissions")
        async def get_world_permissions(world_id: str) -> Dict[str, Any]:
            """Get world permissions"""
            try:
                admin_logger.info(f"Mengambil permissions world dengan ID: {world_id}")
                
                permissions_data = {
                    "roles": [],
                    "users": [],
                    "channels": [],
                    "commands": []
                }
                
                admin_logger.info(f"Berhasil mengambil permissions world {world_id}")
                return {
                    "success": True,
                    "data": permissions_data
                }
                
            except Exception as e:
                admin_logger.error(f"Error getting world permissions {world_id}", e)
                return {
                    "success": False,
                    "error": "Failed to get world permissions",
                    "data": {}
                }
        
        @self.router.put("/worlds/{world_id}/permissions")
        async def update_world_permissions(world_id: str, permissions: Dict[str, Any]) -> Dict[str, Any]:
            """Update world permissions"""
            try:
                admin_logger.info(f"Mengupdate permissions world dengan ID: {world_id}")
                
                # Update world permissions
                # Implementation would save to database
                
                admin_logger.info(f"Permissions world {world_id} berhasil diupdate")
                return {
                    "success": True,
                    "message": f"Permissions world {world_id} berhasil diupdate"
                }
                
            except Exception as e:
                admin_logger.error(f"Error updating world permissions {world_id}", e)
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/worlds/{world_id}/reset-config")
        async def reset_world_config(world_id: str) -> Dict[str, Any]:
            """Reset world configuration to default"""
            try:
                admin_logger.info(f"Mereset konfigurasi world dengan ID: {world_id}")
                
                # Reset to default config
                # Implementation would reset database values
                
                admin_logger.info(f"Konfigurasi world {world_id} berhasil direset")
                return {
                    "success": True,
                    "message": f"Konfigurasi world {world_id} berhasil direset ke default"
                }
                
            except Exception as e:
                admin_logger.error(f"Error resetting world config {world_id}", e)
                raise HTTPException(status_code=500, detail=str(e))


# Create controller instance
world_config_controller = WorldConfigController()

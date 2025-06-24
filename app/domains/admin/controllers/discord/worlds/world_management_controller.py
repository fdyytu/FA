"""
World Management Controller - Manajemen Discord worlds/servers
Dipecah dari discord_worlds_controller.py untuk meningkatkan maintainability
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from app.common.logging.admin_logger import admin_logger
from app.domains.discord.services.bot_manager import bot_manager


class WorldManagementController:
    """Controller untuk manajemen Discord worlds/servers"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        admin_logger.info("WorldManagementController initialized")
    
    def _setup_routes(self):
        """Setup world management routes"""
        
        @self.router.get("/worlds")
        async def get_discord_worlds() -> Dict[str, Any]:
            """Get Discord worlds/servers"""
            try:
                admin_logger.info("Mengambil daftar Discord worlds/servers")
                
                bot_status = bot_manager.get_bot_status()
                guilds = bot_status.get("guilds", [])
                
                worlds_data = []
                for guild in guilds:
                    world_data = {
                        "id": guild.get("id"),
                        "name": guild.get("name"),
                        "players": guild.get("member_count", 0),
                        "status": "online",
                        "owner_id": guild.get("owner_id"),
                        "icon": guild.get("icon"),
                        "created_at": guild.get("created_at"),
                        "features": guild.get("features", [])
                    }
                    worlds_data.append(world_data)
                
                admin_logger.info(f"Berhasil mengambil {len(worlds_data)} Discord worlds")
                return {
                    "success": True,
                    "data": worlds_data
                }
                
            except Exception as e:
                admin_logger.error("Error getting Discord worlds", e)
                return {
                    "success": False,
                    "error": "Failed to get Discord worlds",
                    "data": []
                }
        
        @self.router.get("/worlds/{world_id}")
        async def get_world_details(world_id: str) -> Dict[str, Any]:
            """Get specific world details"""
            try:
                admin_logger.info(f"Mengambil detail world dengan ID: {world_id}")
                
                bot_status = bot_manager.get_bot_status()
                guilds = bot_status.get("guilds", [])
                
                world = None
                for guild in guilds:
                    if str(guild.get("id")) == world_id:
                        world = guild
                        break
                
                if not world:
                    admin_logger.warning(f"World tidak ditemukan untuk ID: {world_id}")
                    raise HTTPException(status_code=404, detail="World not found")
                
                world_data = {
                    "id": world.get("id"),
                    "name": world.get("name"),
                    "description": world.get("description"),
                    "players": world.get("member_count", 0),
                    "status": "online",
                    "owner_id": world.get("owner_id"),
                    "icon": world.get("icon"),
                    "banner": world.get("banner"),
                    "created_at": world.get("created_at"),
                    "features": world.get("features", []),
                    "channels_count": len(world.get("channels", [])),
                    "roles_count": len(world.get("roles", []))
                }
                
                admin_logger.info(f"Berhasil mengambil detail world {world.get('name')}")
                return {
                    "success": True,
                    "data": world_data
                }
                
            except HTTPException:
                raise
            except Exception as e:
                admin_logger.error(f"Error getting world details {world_id}", e)
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/worlds/{world_id}/members")
        async def get_world_members(world_id: str) -> Dict[str, Any]:
            """Get world members"""
            try:
                admin_logger.info(f"Mengambil member world dengan ID: {world_id}")
                
                # Get members data from bot manager
                members_data = []
                
                admin_logger.info(f"Berhasil mengambil {len(members_data)} members")
                return {
                    "success": True,
                    "data": members_data
                }
                
            except Exception as e:
                admin_logger.error(f"Error getting world members {world_id}", e)
                return {
                    "success": False,
                    "error": "Failed to get world members",
                    "data": []
                }


# Create controller instance
world_management_controller = WorldManagementController()

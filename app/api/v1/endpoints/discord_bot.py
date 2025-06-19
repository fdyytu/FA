
from fastapi import APIRouter
from typing import Dict, Any
import logging

from app.domains.discord.controllers.discord_bot_controller import DiscordBotController

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/status")
async def get_bot_status() -> Dict[str, Any]:
    """Get Discord bot status"""
    return await DiscordBotController.get_bot_status()

@router.post("/start")
async def start_bot() -> Dict[str, Any]:
    """Start Discord bot"""
    return await DiscordBotController.start_bot()

@router.post("/stop")
async def stop_bot() -> Dict[str, Any]:
    """Stop Discord bot"""
    return await DiscordBotController.stop_bot()

@router.post("/restart")
async def restart_bot() -> Dict[str, Any]:
    """Restart Discord bot"""
    return await DiscordBotController.restart_bot()

@router.post("/send-message")
async def send_message(channel_id: int, message: str) -> Dict[str, Any]:
    """Send message to Discord channel"""
    return await DiscordBotController.send_message(channel_id, message)

@router.get("/health")
async def bot_health_check() -> Dict[str, Any]:
    """Check Discord bot health"""
    return await DiscordBotController.bot_health_check()

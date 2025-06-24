"""
Discord controllers package
Berisi semua controller Discord yang sudah dipecah menjadi modul kecil
"""

from app.domains.admin.controllers.discord.discord_stats_controller import discord_stats_controller
from app.domains.admin.controllers.discord.discord_bots_controller import discord_bots_controller
from app.domains.admin.controllers.discord.discord_worlds_controller import discord_worlds_controller

__all__ = [
    'discord_stats_controller',
    'discord_bots_controller', 
    'discord_worlds_controller'
]

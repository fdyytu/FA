"""
Routes Package
Package untuk semua route modules
"""

from .static_routes import register_static_routes
from .auth_routes import register_auth_routes
from .admin_routes import register_admin_routes
from .discord_routes import register_discord_routes

__all__ = [
    'register_static_routes',
    'register_auth_routes', 
    'register_admin_routes',
    'register_discord_routes'
]

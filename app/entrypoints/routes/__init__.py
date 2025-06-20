"""
Routes Package
Package yang berisi semua route modules yang telah dipecah
"""

from .static_routes import register_static_routes
from .auth_routes import register_auth_routes
from .discord_routes import register_discord_routes
from .admin_routes import register_admin_routes
from .api_routes import register_api_routes

__all__ = [
    'register_static_routes',
    'register_auth_routes', 
    'register_discord_routes',
    'register_admin_routes',
    'register_api_routes'
]

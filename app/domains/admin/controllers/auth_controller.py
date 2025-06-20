"""
Modul ini sekarang hanya berperan sebagai re-export dari auth modules.
Implementasi telah dipindahkan ke modul terpisah di folder auth/.
"""

from app.domains.admin.controllers.auth import auth_router

# Re-export
router = auth_router
auth_controller = type('AuthController', (), {'router': router})()

__all__ = ['router', 'auth_controller']

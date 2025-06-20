"""
Notification Controllers Package
Package yang berisi semua notification controller modules yang telah dipecah
"""

# Import semua controllers dari modul terpisah
from .user_notification_controller import router as user_notification_router
from .admin_notification_controller import router as admin_notification_router
from .webhook_controller import router as webhook_router
from .test_notification_controller import router as test_notification_router

# Export semua routers untuk backward compatibility
__all__ = [
    'user_notification_router',
    'admin_notification_router',
    'webhook_router',
    'test_notification_router'
]

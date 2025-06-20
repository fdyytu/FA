"""
Modul notification services yang telah dipecah menjadi beberapa file terpisah
untuk meningkatkan maintainability dan mengikuti prinsip Single Responsibility.
"""

from .notification_core_service import NotificationService
from .notification_channel_service import NotificationChannelService
from .admin_notification_service import AdminNotificationService
from .webhook_service import WebhookService

__all__ = [
    'NotificationService',
    'NotificationChannelService', 
    'AdminNotificationService',
    'WebhookService'
]

# Dokumentasi untuk setiap service:

# NotificationService
# - Mengelola CRUD operasi untuk notifikasi user
# - Menandai notifikasi sebagai sudah dibaca

# NotificationChannelService  
# - Mengirim notifikasi ke berbagai channel (Email, Discord, Telegram)
# - Mengikuti prinsip Open/Closed untuk extensibility

# AdminNotificationService
# - Mengelola notifikasi khusus admin
# - Mengatur pengaturan notifikasi per admin

# WebhookService
# - Mengelola webhook dari provider eksternal
# - Memproses dan log webhook requests

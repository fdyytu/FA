"""
Callback System
Sistem callback yang terorganisir untuk mengelola berbagai jenis callback dan webhook
"""

# Base handlers
from app.callbacks.base.base_handlers import (
    BaseCallbackHandler,
    WebhookCallbackHandler,
    EventCallbackHandler,
    CallbackRegistry,
    callback_registry
)

# Payment callbacks
from app.callbacks.payment.midtrans_callback import MidtransCallbackHandler

# PPOB callbacks
from app.callbacks.ppob.ppob_callbacks import (
    DigiflazzCallbackHandler,
    PPOBCallbackFactory
)

# Discord callbacks
from app.callbacks.discord.discord_callbacks import (
    DiscordBotEventHandler,
    DiscordSlashCommandHandler
)

# File monitor callbacks
from app.callbacks.file_monitor.file_callbacks import (
    FileMonitorCallbackHandler,
    FileUploadCallbackHandler
)

# Notification callbacks
from app.callbacks.notification.notification_callbacks import (
    NotificationWebhookHandler,
    DiscordWebhookHandler,
    TelegramWebhookHandler,
    NotificationCallbackFactory
)

# Callback manager
from app.callbacks.callback_manager import (
    CallbackManager,
    CallbackRouter,
    get_callback_manager,
    initialize_callbacks
)

# Callback controller
from app.callbacks.callback_controller import (
    CallbackController,
    callback_controller,
    router as callback_router
)

__all__ = [
    # Base handlers
    "BaseCallbackHandler",
    "WebhookCallbackHandler", 
    "EventCallbackHandler",
    "CallbackRegistry",
    "callback_registry",
    
    # Payment callbacks
    "MidtransCallbackHandler",
    
    # PPOB callbacks
    "DigiflazzCallbackHandler",
    "PPOBCallbackFactory",
    
    # Discord callbacks
    "DiscordBotEventHandler",
    "DiscordSlashCommandHandler",
    
    # File monitor callbacks
    "FileMonitorCallbackHandler",
    "FileUploadCallbackHandler",
    
    # Notification callbacks
    "NotificationWebhookHandler",
    "DiscordWebhookHandler",
    "TelegramWebhookHandler",
    "NotificationCallbackFactory",
    
    # Callback manager
    "CallbackManager",
    "CallbackRouter",
    "get_callback_manager",
    "initialize_callbacks",
    
    # Callback controller
    "CallbackController",
    "callback_controller",
    "callback_router"
]

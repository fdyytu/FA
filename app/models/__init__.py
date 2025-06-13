"""Models package."""
from app.models.base import Base, BaseModel
from app.models.user import User
from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, TransactionStatus, PPOBCategory
from app.models.file_event import FileEvent
from app.models.wallet import (
    WalletTransaction, Transfer, TopUpRequest,
    TransactionType, PaymentMethod, TopUpStatus
)
from app.models.admin import Admin, AdminConfig, PPOBMarginConfig, MarginType
from app.models.transaction import Transaction, UserProfile, DailyMutation, TransactionType as NewTransactionType, TransactionStatus as NewTransactionStatus
from app.models.notification import (
    Notification, AdminNotificationSetting, WebhookLog,
    NotificationType, NotificationChannel, NotificationStatus
)
from app.models.product import Product, ProductStock

__all__ = [
    "Base",
    "BaseModel", 
    "User",
    "PPOBTransaction",
    "PPOBProduct",
    "TransactionStatus",
    "PPOBCategory",
    "FileEvent",
    "WalletTransaction",
    "Transfer",
    "TopUpRequest",
    "TransactionType",
    "PaymentMethod",
    "TopUpStatus",
    "Admin",
    "AdminConfig",
    "PPOBMarginConfig",
    "MarginType",
    "Transaction",
    "UserProfile",
    "DailyMutation",
    "NewTransactionType",
    "NewTransactionStatus",
    "Notification",
    "AdminNotificationSetting",
    "WebhookLog",
    "NotificationType",
    "NotificationChannel",
    "NotificationStatus",
    "Product",
    "ProductStock"
]


# Discord Models
from .discord import *

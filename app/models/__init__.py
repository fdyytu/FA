"""Models package."""
from app.models.base import Base, BaseModel

# Import models from domains
from app.domains.user.models.user import User
from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, TransactionStatus, PPOBCategory
from app.domains.wallet.models.wallet import (
    WalletTransaction, Transfer, TopUpRequest,
    TransactionType, PaymentMethod, TopUpStatus
)
from app.domains.admin.models.admin import Admin, AdminConfig, PPOBMarginConfig, MarginType
from app.domains.transaction.models.transaction import Transaction, UserProfile, DailyMutation, TransactionType as NewTransactionType, TransactionStatus as NewTransactionStatus
from app.domains.notification.models.notification import (
    Notification, AdminNotificationSetting, WebhookLog,
    NotificationType, NotificationChannel, NotificationStatus
)
from app.domains.product.models.product import Product, ProductStock
from app.domains.file_monitor.models.file_event import FileEvent

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

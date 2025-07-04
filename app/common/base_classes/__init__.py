"""Models package."""
from app.common.base_classes.base import Base, BaseModel

# Import models from domains that exist
try:
    from app.domains.auth.models.user import User
except ImportError:
    User = None

try:
    from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, TransactionStatus, PPOBCategory
except ImportError:
    PPOBTransaction = PPOBProduct = TransactionStatus = PPOBCategory = None

try:
    from app.domains.admin.models.admin import Admin, AdminConfig, PPOBMarginConfig, MarginType
except ImportError:
    Admin = AdminConfig = PPOBMarginConfig = MarginType = None

__all__ = [
    "Base",
    "BaseModel"
]

# Add to __all__ only if imported successfully
if User:
    __all__.append("User")
if PPOBTransaction:
    __all__.extend(["PPOBTransaction", "PPOBProduct", "TransactionStatus", "PPOBCategory"])
if Admin:
    __all__.extend(["Admin", "AdminConfig", "PPOBMarginConfig", "MarginType"])

"""
Admin schemas components package
Berisi semua schema yang sudah dipecah menjadi modul kecil
"""

# Import semua schemas dari modul terpisah
from .admin_schemas import *
from .user_management_schemas import *
from .product_management_schemas import *
from .configuration_schemas import *
from .dashboard_schemas import *
from .common_schemas import *
from .discord_schemas import *

__all__ = [
    # Admin schemas
    'AdminRole', 'AdminBase', 'AdminCreate', 'AdminUpdate', 'AdminResponse', 
    'AdminLogin', 'AdminLoginResponse',
    
    # User management schemas
    'UserManagementResponse', 'UserUpdateByAdmin',
    
    # Product management schemas
    'ProductCreate', 'ProductUpdate', 'ProductResponse',
    
    # Configuration schemas
    'MarginType', 'ConfigCreate', 'ConfigUpdate', 'ConfigResponse',
    'MarginConfigCreate', 'MarginConfigUpdate', 'MarginConfigResponse',
    
    # Dashboard schemas
    'DashboardStats', 'TransactionStats', 'DashboardResponse',
    
    # Common schemas
    'PaginationParams', 'PaginatedResponse', 'AuditLogResponse',
    'ProviderConfig', 'ProviderResponse',
    
    # Discord schemas
    'DiscordConfigCreate', 'DiscordConfigUpdate', 'DiscordConfigResponse'
]

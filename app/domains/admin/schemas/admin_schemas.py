"""
Admin Schemas - Versi baru yang menggunakan components
Menggantikan admin_schemas.py yang besar dengan composition pattern
"""

# Import semua schemas dari components
from app.domains.admin.schemas.components import *

# Re-export semua untuk backward compatibility
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

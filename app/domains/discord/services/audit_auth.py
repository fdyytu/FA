# Audit Logger Helper Functions - Authentication Operations
from .audit_logger import audit_logger_service

def log_auth_failure(user_id: str, reason: str, ip_address: str):
    """Log authentication failures"""
    return audit_logger_service.log_admin_action(
        user_id=user_id,
        action="auth_failure",
        resource="discord_auth",
        details={"failure_reason": reason},
        ip_address=ip_address
    )

def log_permission_denied(user_id: str, attempted_action: str, ip_address: str):
    """Log permission denied events"""
    return audit_logger_service.log_admin_action(
        user_id=user_id,
        action="permission_denied",
        resource="discord_permissions",
        details={"attempted_action": attempted_action},
        ip_address=ip_address
    )

def log_token_refresh(user_id: str, ip_address: str, success: bool):
    """Log token refresh attempts"""
    action = "token_refresh_success" if success else "token_refresh_failed"
    return audit_logger_service.log_admin_action(
        user_id=user_id,
        action=action,
        resource="discord_token",
        details={"refresh_success": success},
        ip_address=ip_address
    )

# Audit Logger Helper Functions - Security Operations
from .audit_logger import audit_logger_service
from typing import Optional

def log_security_event(event_type: str, user_id: str, details: dict, ip_address: Optional[str] = None):
    """Log security-related events"""
    return audit_logger_service.log_admin_action(
        user_id=user_id,
        action=f"security_{event_type}",
        resource="discord_security",
        details=details,
        ip_address=ip_address
    )

def log_admin_login(user_id: str, ip_address: str, success: bool):
    """Log admin login attempts"""
    action = "admin_login_success" if success else "admin_login_failed"
    return audit_logger_service.log_admin_action(
        user_id=user_id,
        action=action,
        resource="discord_admin_auth",
        details={"login_success": success},
        ip_address=ip_address
    )

def log_rate_limit_violation(user_id: str, operation_type: str, ip_address: str):
    """Log rate limit violations"""
    return audit_logger_service.log_admin_action(
        user_id=user_id,
        action="rate_limit_violation",
        resource="discord_rate_limit",
        details={"operation_type": operation_type, "violation_type": "exceeded_limit"},
        ip_address=ip_address
    )

# Audit Logger Helper Functions - Bot Operations
from .audit_logger import audit_logger_service

def log_bot_action(bot_id: str, action: str, user_id: str, result: str):
    """Log bot-specific actions"""
    return audit_logger_service.log_admin_action(
        user_id=user_id,
        action=f"bot_{action}",
        resource=f"discord_bot_{bot_id}",
        details={"bot_id": bot_id, "result": result}
    )

def log_bulk_operation(operation: str, user_id: str, bot_count: int, success_count: int):
    """Log bulk operations"""
    return audit_logger_service.log_admin_action(
        user_id=user_id,
        action=f"bulk_{operation}",
        resource="discord_bots_bulk",
        details={
            "operation": operation,
            "total_bots": bot_count,
            "successful": success_count,
            "failed": bot_count - success_count
        }
    )

def log_config_change(config_id: str, user_id: str, changes: dict):
    """Log configuration changes"""
    return audit_logger_service.log_admin_action(
        user_id=user_id,
        action="config_update",
        resource=f"discord_config_{config_id}",
        details={"changes": changes}
    )

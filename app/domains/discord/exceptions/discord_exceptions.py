from typing import Optional, Dict, Any

class DiscordBaseException(Exception):
    """Base exception untuk semua Discord operations"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "DISCORD_ERROR"
        self.details = details or {}
        super().__init__(self.message)

class BotNotFoundError(DiscordBaseException):
    """Exception ketika bot tidak ditemukan"""
    def __init__(self, bot_id: str):
        super().__init__(
            message=f"Bot dengan ID {bot_id} tidak ditemukan",
            error_code="BOT_NOT_FOUND",
            details={"bot_id": bot_id}
        )

class BotConnectionError(DiscordBaseException):
    """Exception ketika bot gagal connect ke Discord"""
    def __init__(self, bot_id: str, reason: str = None):
        super().__init__(
            message=f"Bot {bot_id} gagal connect: {reason or 'Unknown error'}",
            error_code="BOT_CONNECTION_ERROR",
            details={"bot_id": bot_id, "reason": reason}
        )

class InvalidConfigurationError(DiscordBaseException):
    """Exception ketika konfigurasi bot tidak valid"""
    def __init__(self, config_field: str, reason: str = None):
        super().__init__(
            message=f"Konfigurasi tidak valid pada field '{config_field}': {reason or 'Invalid value'}",
            error_code="INVALID_CONFIGURATION",
            details={"field": config_field, "reason": reason}
        )

class RateLimitExceededError(DiscordBaseException):
    """Exception ketika rate limit terlampaui"""
    def __init__(self, operation: str, retry_after: int = None):
        super().__init__(
            message=f"Rate limit exceeded untuk operasi '{operation}'",
            error_code="RATE_LIMIT_EXCEEDED",
            details={"operation": operation, "retry_after": retry_after}
        )

class UnauthorizedOperationError(DiscordBaseException):
    """Exception ketika operasi tidak diizinkan"""
    def __init__(self, operation: str, user_id: str = None):
        super().__init__(
            message=f"Operasi '{operation}' tidak diizinkan",
            error_code="UNAUTHORIZED_OPERATION",
            details={"operation": operation, "user_id": user_id}
        )

class BulkOperationError(DiscordBaseException):
    """Exception untuk error dalam bulk operations"""
    def __init__(self, failed_operations: list, total_operations: int):
        super().__init__(
            message=f"Bulk operation gagal: {len(failed_operations)}/{total_operations} operasi gagal",
            error_code="BULK_OPERATION_ERROR",
            details={"failed_count": len(failed_operations), "total_count": total_operations, "failed_operations": failed_operations}
        )

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime

from ..exceptions.discord_exceptions import (
    DiscordBaseException, BotNotFoundError, BotConnectionError,
    InvalidConfigurationError, RateLimitExceededError,
    UnauthorizedOperationError, BulkOperationError
)

logger = logging.getLogger(__name__)

class DiscordErrorHandler:
    """Global error handler untuk Discord operations"""
    
    @staticmethod
    def format_error_response(exception: DiscordBaseException) -> Dict[str, Any]:
        """Format error response untuk client"""
        return {
            "success": False,
            "error": {
                "code": exception.error_code,
                "message": exception.message,
                "details": exception.details,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    async def handle_discord_exception(request: Request, exc: DiscordBaseException):
        """Handle Discord-specific exceptions"""
        logger.error(f"Discord error: {exc.error_code} - {exc.message}")
        
        # Tentukan HTTP status code berdasarkan jenis error
        status_code = 500  # Default server error
        
        if isinstance(exc, BotNotFoundError):
            status_code = 404
        elif isinstance(exc, InvalidConfigurationError):
            status_code = 400
        elif isinstance(exc, RateLimitExceededError):
            status_code = 429
        elif isinstance(exc, UnauthorizedOperationError):
            status_code = 403
        elif isinstance(exc, BotConnectionError):
            status_code = 503
        elif isinstance(exc, BulkOperationError):
            status_code = 207  # Multi-status
            
        response_data = DiscordErrorHandler.format_error_response(exc)
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    @staticmethod
    async def handle_general_exception(request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        
        response_data = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Terjadi kesalahan internal server",
                "details": {"original_error": str(exc)},
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return JSONResponse(
            status_code=500,
            content=response_data
        )

# Global instance
discord_error_handler = DiscordErrorHandler()

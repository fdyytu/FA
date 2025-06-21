"""
Endpoint Logging Utilities
Menyediakan decorator dan utility functions untuk logging endpoint-specific errors
"""

import logging
import functools
import traceback
from typing import Any, Callable, Optional
from fastapi import Request, HTTPException


def get_endpoint_logger(endpoint_path: str) -> logging.Logger:
    """
    Get logger khusus untuk endpoint tertentu
    
    Args:
        endpoint_path: Path endpoint (e.g., "/api/v1/admin/login")
        
    Returns:
        Logger instance untuk endpoint
    """
    # Normalize path untuk logger name
    logger_name = f"endpoint{endpoint_path.replace('/', '.')}"
    return logging.getLogger(logger_name)


def log_endpoint_error(endpoint_path: str, error: Exception, request: Optional[Request] = None, **context):
    """
    Log error yang terjadi di endpoint tertentu
    
    Args:
        endpoint_path: Path endpoint
        error: Exception yang terjadi
        request: FastAPI Request object (optional)
        **context: Additional context untuk logging
    """
    logger = get_endpoint_logger(endpoint_path)
    
    # Build error context
    error_context = {
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "endpoint": endpoint_path,
        **context
    }
    
    # Add request context if available
    if request:
        error_context.update({
            "method": request.method,
            "client_ip": _get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "N/A"),
            "query_params": dict(request.query_params)
        })
    
    # Log dengan level yang sesuai
    if isinstance(error, HTTPException):
        if error.status_code < 500:
            logger.warning(
                f"🟡 HTTP Error {error.status_code} in {endpoint_path}: {error.detail}",
                extra={"error_context": error_context}
            )
        else:
            logger.error(
                f"🔴 HTTP Error {error.status_code} in {endpoint_path}: {error.detail}",
                extra={"error_context": error_context}
            )
    elif isinstance(error, (ImportError, ModuleNotFoundError)):
        logger.error(
            f"🚫 Module Error in {endpoint_path}: {error.__class__.__name__}: {str(error)}",
            extra={
                "error_context": error_context,
                "traceback": traceback.format_exc()
            }
        )
    else:
        logger.error(
            f"💥 Unexpected Error in {endpoint_path}: {error.__class__.__name__}: {str(error)}",
            extra={
                "error_context": error_context,
                "traceback": traceback.format_exc()
            }
        )


def log_endpoint_access(endpoint_path: str, request: Request, **context):
    """
    Log akses ke endpoint
    
    Args:
        endpoint_path: Path endpoint
        request: FastAPI Request object
        **context: Additional context
    """
    logger = get_endpoint_logger(endpoint_path)
    
    access_context = {
        "endpoint": endpoint_path,
        "method": request.method,
        "client_ip": _get_client_ip(request),
        "user_agent": request.headers.get("user-agent", "N/A"),
        "query_params": dict(request.query_params),
        **context
    }
    
    logger.info(
        f"🔵 Accessing {request.method} {endpoint_path}",
        extra={"access_context": access_context}
    )


def log_module_import_error(module_name: str, error: Exception, context: str = ""):
    """
    Log error saat import module
    
    Args:
        module_name: Nama module yang gagal di-import
        error: Exception yang terjadi
        context: Context tambahan (e.g., "router registration")
    """
    logger = logging.getLogger("module_import")
    
    error_context = {
        "module_name": module_name,
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "context": context,
        "traceback": traceback.format_exc()
    }
    
    logger.error(
        f"🚫 Failed to import module '{module_name}': {error.__class__.__name__}: {str(error)}",
        extra={"import_error": error_context}
    )


def endpoint_logger(endpoint_path: Optional[str] = None):
    """
    Decorator untuk automatic endpoint logging
    
    Args:
        endpoint_path: Path endpoint (optional, akan di-detect otomatis)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request and 'request' in kwargs:
                request = kwargs['request']
            
            # Determine endpoint path
            path = endpoint_path
            if not path and request:
                path = request.url.path
            elif not path:
                path = func.__name__
            
            # Log access
            if request:
                log_endpoint_access(path, request)
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Log success
                logger = get_endpoint_logger(path)
                logger.info(f"✅ Successfully processed {path}")
                
                return result
                
            except Exception as error:
                # Log error
                log_endpoint_error(path, error, request)
                raise
        
        return wrapper
    return decorator


def _get_client_ip(request: Request) -> str:
    """Get real client IP address"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


class EndpointLogger:
    """
    Context manager untuk endpoint logging
    """
    
    def __init__(self, endpoint_path: str, request: Optional[Request] = None):
        self.endpoint_path = endpoint_path
        self.request = request
        self.logger = get_endpoint_logger(endpoint_path)
    
    def __enter__(self):
        if self.request:
            log_endpoint_access(self.endpoint_path, self.request)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            log_endpoint_error(self.endpoint_path, exc_val, self.request)
        else:
            self.logger.info(f"✅ Successfully completed {self.endpoint_path}")
    
    def info(self, message: str, **context):
        """Log info message"""
        self.logger.info(f"ℹ️ {message}", extra={"context": context})
    
    def warning(self, message: str, **context):
        """Log warning message"""
        self.logger.warning(f"⚠️ {message}", extra={"context": context})
    
    def error(self, message: str, **context):
        """Log error message"""
        self.logger.error(f"❌ {message}", extra={"context": context})

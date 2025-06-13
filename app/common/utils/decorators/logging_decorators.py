"""
Logging related decorators
Decorators untuk logging, execution time, dan audit trail
"""

import time
import functools
import asyncio
import logging
from typing import Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def log_execution_time(func_name: Optional[str] = None):
    """
    Decorator untuk log execution time
    
    Args:
        func_name: Custom nama function untuk logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Function {name} executed in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Function {name} failed after {execution_time:.4f}s: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Function {name} executed in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Function {name} failed after {execution_time:.4f}s: {e}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def audit_log(action: str, resource_type: str):
    """
    Decorator untuk audit logging
    
    Args:
        action: Action yang dilakukan (CREATE, UPDATE, DELETE, etc.)
        resource_type: Type of resource
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            user_id = kwargs.get('user_id') or kwargs.get('current_user_id', 'system')
            
            try:
                result = await func(*args, **kwargs)
                
                # Log successful action
                logger.info(
                    f"AUDIT: {action} {resource_type} by user {user_id} - SUCCESS",
                    extra={
                        "audit": {
                            "action": action,
                            "resource_type": resource_type,
                            "user_id": user_id,
                            "execution_time": time.time() - start_time,
                            "status": "SUCCESS",
                            "function": func.__name__
                        }
                    }
                )
                
                return result
                
            except Exception as e:
                # Log failed action
                logger.warning(
                    f"AUDIT: {action} {resource_type} by user {user_id} - FAILED: {str(e)}",
                    extra={
                        "audit": {
                            "action": action,
                            "resource_type": resource_type,
                            "user_id": user_id,
                            "execution_time": time.time() - start_time,
                            "status": "FAILED",
                            "error": str(e),
                            "function": func.__name__
                        }
                    }
                )
                raise
        
        return wrapper
    return decorator


def deprecated(reason: str = "", version: str = ""):
    """
    Decorator untuk mark function sebagai deprecated
    
    Args:
        reason: Reason for deprecation
        version: Version when deprecated
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            warning_msg = f"Function {func.__name__} is deprecated"
            if version:
                warning_msg += f" since version {version}"
            if reason:
                warning_msg += f": {reason}"
            
            logger.warning(warning_msg)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

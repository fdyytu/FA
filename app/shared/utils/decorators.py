"""
Decorators untuk implementasi DRY principle dan cross-cutting concerns
Reusable decorators untuk logging, caching, validation, dll
"""

import time
import functools
import asyncio
from typing import Any, Callable, Dict, Optional, Union, List
from functools import wraps
import logging
from app.core.constants import CacheKeys, StatusMessages
from app.utils.exceptions import ValidationException, UnauthorizedError, ForbiddenError

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


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator untuk retry mechanism
    
    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier
        exceptions: Tuple of exceptions to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def cache_result(key_template: str, expire_seconds: int = 300):
    """
    Decorator untuk caching function results
    
    Args:
        key_template: Template untuk cache key (support format strings)
        expire_seconds: Cache expiration time
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            try:
                # Combine args dan kwargs untuk key generation
                key_data = {
                    'args': args,
                    'kwargs': kwargs,
                    'func_name': func.__name__
                }
                cache_key = key_template.format(**key_data, **kwargs)
            except (KeyError, ValueError):
                # Fallback ke simple key jika template gagal
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            try:
                from app.core.container import get_service
                from app.core.interfaces import ICacheService
                
                cache_service = get_service(ICacheService)
                cached_result = await cache_service.get(cache_key)
                
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                    return cached_result
                    
            except Exception as e:
                logger.warning(f"Cache get failed for {func.__name__}: {e}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                await cache_service.set(cache_key, result, expire_seconds)
                logger.debug(f"Cached result for {func.__name__}: {cache_key}")
            except Exception as e:
                logger.warning(f"Cache set failed for {func.__name__}: {e}")
            
            return result
        
        return wrapper
    return decorator


def validate_input(**validators):
    """
    Decorator untuk input validation
    
    Args:
        **validators: Dict of parameter_name -> validator_function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            errors = []
            
            # Validate kwargs
            for param_name, validator in validators.items():
                if param_name in kwargs:
                    try:
                        if not validator(kwargs[param_name]):
                            errors.append(f"Invalid value for {param_name}")
                    except Exception as e:
                        errors.append(f"Validation error for {param_name}: {str(e)}")
            
            if errors:
                raise ValidationException("Input validation failed", errors=errors)
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            errors = []
            
            # Validate kwargs
            for param_name, validator in validators.items():
                if param_name in kwargs:
                    try:
                        if not validator(kwargs[param_name]):
                            errors.append(f"Invalid value for {param_name}")
                    except Exception as e:
                        errors.append(f"Validation error for {param_name}: {str(e)}")
            
            if errors:
                raise ValidationException("Input validation failed", errors=errors)
            
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def require_permissions(*required_permissions):
    """
    Decorator untuk authorization check
    
    Args:
        *required_permissions: List of required permissions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user dari kwargs atau args
            user = kwargs.get('current_user') or kwargs.get('user')
            
            if not user:
                # Try to get from first argument (common pattern)
                if args and hasattr(args[0], 'permissions'):
                    user = args[0]
                else:
                    raise UnauthorizedError("User not authenticated")
            
            # Check permissions
            user_permissions = getattr(user, 'permissions', [])
            
            for permission in required_permissions:
                if permission not in user_permissions:
                    raise ForbiddenError(f"Missing required permission: {permission}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def rate_limit(requests_per_minute: int = 60, key_func: Optional[Callable] = None):
    """
    Decorator untuk rate limiting
    
    Args:
        requests_per_minute: Maximum requests per minute
        key_func: Function untuk generate rate limit key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                rate_key = key_func(*args, **kwargs)
            else:
                # Default key based on function name dan user
                user_id = kwargs.get('user_id', 'anonymous')
                rate_key = f"rate_limit:{func.__name__}:{user_id}"
            
            try:
                from app.core.container import get_service
                from app.core.interfaces import ICacheService
                
                cache_service = get_service(ICacheService)
                
                # Check current count
                current_count = await cache_service.get(rate_key) or 0
                
                if current_count >= requests_per_minute:
                    raise ForbiddenError(StatusMessages.RATE_LIMIT_EXCEEDED)
                
                # Increment counter
                await cache_service.set(rate_key, current_count + 1, 60)  # 1 minute expiry
                
            except Exception as e:
                logger.warning(f"Rate limiting failed for {func.__name__}: {e}")
                # Continue execution jika rate limiting gagal
            
            return await func(*args, **kwargs)
        
        return wrapper
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


def transaction_required(func: Callable) -> Callable:
    """
    Decorator untuk ensure database transaction
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Check if db session exists in kwargs
        db = kwargs.get('db')
        
        if not db:
            # Try to get from dependency injection
            try:
                from app.core.database import get_db
                db = next(get_db())
                kwargs['db'] = db
            except Exception as e:
                logger.error(f"Failed to get database session: {e}")
                raise
        
        try:
            result = await func(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    
    return wrapper


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


# Utility decorators untuk common validations
def validate_positive_number(value: Union[int, float]) -> bool:
    """Validator untuk positive numbers"""
    return isinstance(value, (int, float)) and value > 0


def validate_email(email: str) -> bool:
    """Simple email validator"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Simple phone validator"""
    import re
    # Indonesian phone number pattern
    pattern = r'^(\+62|62|0)[0-9]{9,13}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))


def validate_non_empty_string(value: str) -> bool:
    """Validator untuk non-empty strings"""
    return isinstance(value, str) and len(value.strip()) > 0

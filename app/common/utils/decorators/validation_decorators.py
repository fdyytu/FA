"""
Validation and security decorators
Decorators untuk input validation, authorization, dan security
"""

import asyncio
import logging
from typing import Callable, Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)


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
                from app.common.exceptions.custom_exceptions import ValidationException
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
                from app.common.exceptions.custom_exceptions import ValidationException
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
                    from app.common.exceptions.custom_exceptions import UnauthorizedError
                    raise UnauthorizedError("User not authenticated")
            
            # Check permissions
            user_permissions = getattr(user, 'permissions', [])
            
            for permission in required_permissions:
                if permission not in user_permissions:
                    from app.common.exceptions.custom_exceptions import ForbiddenError
                    raise ForbiddenError(f"Missing required permission: {permission}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_roles(*required_roles):
    """
    Decorator untuk role-based authorization check
    
    Args:
        *required_roles: List of required roles
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user dari kwargs atau args
            user = kwargs.get('current_user') or kwargs.get('user')
            
            if not user:
                from app.common.exceptions.custom_exceptions import UnauthorizedError
                raise UnauthorizedError("User not authenticated")
            
            # Check roles
            user_roles = getattr(user, 'roles', [])
            
            # Check if user has any of the required roles
            has_required_role = any(role in user_roles for role in required_roles)
            
            if not has_required_role:
                from app.common.exceptions.custom_exceptions import ForbiddenError
                raise ForbiddenError(f"Missing required role. Required: {required_roles}, User has: {user_roles}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_schema(schema_class):
    """
    Decorator untuk validate request data menggunakan Pydantic schema
    
    Args:
        schema_class: Pydantic model class untuk validation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Look for data to validate
            data = kwargs.get('data') or kwargs.get('request_data')
            
            if data is not None:
                try:
                    # Validate using Pydantic schema
                    validated_data = schema_class(**data)
                    kwargs['validated_data'] = validated_data
                except Exception as e:
                    from app.common.exceptions.custom_exceptions import ValidationException
                    raise ValidationException(f"Schema validation failed: {str(e)}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def rate_limit(max_calls: int, time_window: int = 60):
    """
    Simple rate limiting decorator
    
    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds
    """
    import time
    from collections import defaultdict, deque
    
    # Store call times per function
    call_times = defaultdict(deque)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = time.time()
            func_name = func.__name__
            
            # Clean old entries
            while call_times[func_name] and call_times[func_name][0] < current_time - time_window:
                call_times[func_name].popleft()
            
            # Check rate limit
            if len(call_times[func_name]) >= max_calls:
                from app.common.exceptions.custom_exceptions import RateLimitError
                raise RateLimitError(f"Rate limit exceeded for {func_name}. Max {max_calls} calls per {time_window} seconds")
            
            # Record this call
            call_times[func_name].append(current_time)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def sanitize_input(fields: Dict[str, Callable] = None):
    """
    Decorator untuk sanitize input data
    
    Args:
        fields: Dict of field_name -> sanitizer_function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if fields:
                for field_name, sanitizer in fields.items():
                    if field_name in kwargs:
                        try:
                            kwargs[field_name] = sanitizer(kwargs[field_name])
                        except Exception as e:
                            logger.warning(f"Failed to sanitize field {field_name}: {e}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

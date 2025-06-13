"""
Retry and resilience decorators
Decorators untuk retry mechanism dan error handling
"""

import time
import asyncio
import logging
from typing import Callable, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


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


def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60, expected_exception: Tuple = (Exception,)):
    """
    Circuit breaker pattern decorator
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time to wait before trying again (seconds)
        expected_exception: Exceptions that count as failures
    """
    def decorator(func: Callable) -> Callable:
        # Circuit breaker state
        state = {
            'failures': 0,
            'last_failure_time': None,
            'state': 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        }
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Check if circuit is open and recovery timeout has passed
            if state['state'] == 'OPEN':
                if current_time - state['last_failure_time'] > recovery_timeout:
                    state['state'] = 'HALF_OPEN'
                    logger.info(f"Circuit breaker for {func.__name__} is now HALF_OPEN")
                else:
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                
                # Reset on success
                if state['state'] == 'HALF_OPEN':
                    state['state'] = 'CLOSED'
                    state['failures'] = 0
                    logger.info(f"Circuit breaker for {func.__name__} is now CLOSED")
                
                return result
                
            except expected_exception as e:
                state['failures'] += 1
                state['last_failure_time'] = current_time
                
                if state['failures'] >= failure_threshold:
                    state['state'] = 'OPEN'
                    logger.warning(f"Circuit breaker for {func.__name__} is now OPEN after {state['failures']} failures")
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Check if circuit is open and recovery timeout has passed
            if state['state'] == 'OPEN':
                if current_time - state['last_failure_time'] > recovery_timeout:
                    state['state'] = 'HALF_OPEN'
                    logger.info(f"Circuit breaker for {func.__name__} is now HALF_OPEN")
                else:
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                # Reset on success
                if state['state'] == 'HALF_OPEN':
                    state['state'] = 'CLOSED'
                    state['failures'] = 0
                    logger.info(f"Circuit breaker for {func.__name__} is now CLOSED")
                
                return result
                
            except expected_exception as e:
                state['failures'] += 1
                state['last_failure_time'] = current_time
                
                if state['failures'] >= failure_threshold:
                    state['state'] = 'OPEN'
                    logger.warning(f"Circuit breaker for {func.__name__} is now OPEN after {state['failures']} failures")
                
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def timeout(seconds: float):
    """
    Timeout decorator for async functions
    
    Args:
        seconds: Timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {seconds} seconds")
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
        
        return wrapper
    return decorator

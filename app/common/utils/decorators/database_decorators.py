"""
Database related decorators
Decorators untuk database transactions dan operations
"""

import logging
from typing import Callable
from functools import wraps

logger = logging.getLogger(__name__)


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
                from app.infrastructure.database.database_manager import get_db
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


def auto_commit(func: Callable) -> Callable:
    """
    Decorator untuk auto commit database changes
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = kwargs.get('db')
        
        if not db:
            logger.warning(f"No database session found in {func.__name__}")
            return await func(*args, **kwargs)
        
        try:
            result = await func(*args, **kwargs)
            db.commit()
            logger.debug(f"Auto-committed changes in {func.__name__}")
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Auto-rollback in {func.__name__}: {e}")
            raise
    
    return wrapper


def read_only_transaction(func: Callable) -> Callable:
    """
    Decorator untuk read-only database operations
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = kwargs.get('db')
        
        if not db:
            try:
                from app.infrastructure.database.database_manager import get_db
                db = next(get_db())
                kwargs['db'] = db
            except Exception as e:
                logger.error(f"Failed to get database session: {e}")
                raise
        
        try:
            # Set read-only mode if supported
            if hasattr(db, 'execute'):
                db.execute("SET TRANSACTION READ ONLY")
            
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error in read-only transaction {func.__name__}: {e}")
            raise
        finally:
            if hasattr(db, 'close'):
                db.close()
    
    return wrapper


def with_database_session(func: Callable) -> Callable:
    """
    Decorator untuk provide database session jika tidak ada
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db_provided = 'db' in kwargs and kwargs['db'] is not None
        
        if not db_provided:
            try:
                from app.infrastructure.database.database_manager import get_db
                db = next(get_db())
                kwargs['db'] = db
            except Exception as e:
                logger.error(f"Failed to get database session: {e}")
                raise
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            # Only close if we provided the session
            if not db_provided and 'db' in kwargs:
                kwargs['db'].close()
    
    return wrapper


def bulk_operation(batch_size: int = 1000):
    """
    Decorator untuk bulk database operations
    
    Args:
        batch_size: Size of each batch
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            items = kwargs.get('items', [])
            
            if not items:
                return await func(*args, **kwargs)
            
            results = []
            
            # Process in batches
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                kwargs['items'] = batch
                
                try:
                    batch_result = await func(*args, **kwargs)
                    results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
                    
                    logger.debug(f"Processed batch {i//batch_size + 1} of {len(items)//batch_size + 1}")
                    
                except Exception as e:
                    logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                    raise
            
            return results
        
        return wrapper
    return decorator

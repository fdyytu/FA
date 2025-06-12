"""
Dependency Injection Container
Implementasi DIP (Dependency Inversion Principle)
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Simple dependency container
_container: Dict[str, Any] = {}

def setup_dependencies():
    """Setup dependency injection container"""
    try:
        # Register dependencies here
        # For now, just log that it's setup
        logger.info("Dependencies configured successfully")
        
    except Exception as e:
        logger.error(f"Error setting up dependencies: {e}")
        raise

def get_dependency(name: str):
    """Get dependency from container"""
    return _container.get(name)

def register_dependency(name: str, instance: Any):
    """Register dependency in container"""
    _container[name] = instance

"""
Core configuration module
"""
from app.infrastructure.config.settings import settings

# Re-export settings for backward compatibility
__all__ = ['settings']

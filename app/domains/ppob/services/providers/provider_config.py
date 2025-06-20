from typing import Dict, Type
from enum import Enum
from datetime import datetime

from app.services.ppob.base import PPOBProviderInterface


class ProviderStatus(Enum):
    """Status provider - Interface Segregation"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"


class ProviderConfig:
    """
    Konfigurasi provider - Single Responsibility: Provider configuration
    """
    def __init__(
        self,
        name: str,
        provider_class: Type[PPOBProviderInterface],
        priority: int,
        config: Dict,
        is_active: bool = True
    ):
        self.name = name
        self.provider_class = provider_class
        self.priority = priority
        self.config = config
        self.is_active = is_active
        self.status = ProviderStatus.HEALTHY
        self.last_health_check = None
        self.error_count = 0
        self.max_errors = 5
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary"""
        return {
            "name": self.name,
            "priority": self.priority,
            "config": self.config,
            "is_active": self.is_active,
            "status": self.status.value,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "error_count": self.error_count,
            "max_errors": self.max_errors
        }
    
    def is_available(self) -> bool:
        """Check if provider is available for use"""
        return (
            self.is_active and 
            self.status in [ProviderStatus.HEALTHY, ProviderStatus.MAINTENANCE]
        )
    
    def increment_error(self) -> None:
        """Increment error count and update status if needed"""
        self.error_count += 1
        if self.error_count >= self.max_errors:
            self.status = ProviderStatus.UNHEALTHY
    
    def reset_errors(self) -> None:
        """Reset error count and set status to healthy"""
        self.error_count = 0
        self.status = ProviderStatus.HEALTHY

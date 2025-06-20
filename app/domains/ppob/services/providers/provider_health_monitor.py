from typing import Dict
import logging
from datetime import datetime

from app.services.ppob.base import PPOBProviderInterface
from .provider_config import ProviderConfig, ProviderStatus


class ProviderHealthMonitor:
    """
    Monitor kesehatan provider - Single Responsibility: Health monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def check_provider_health(self, provider: PPOBProviderInterface) -> bool:
        """Cek kesehatan provider"""
        try:
            # Implementasi health check sederhana
            # Bisa diperluas dengan ping ke API provider
            health_result = await provider.health_check()
            return health_result.get("status") == "healthy"
        except Exception as e:
            self.logger.error(f"Health check failed for provider: {e}")
            return False
    
    async def update_provider_status(
        self, 
        config: ProviderConfig, 
        is_healthy: bool
    ) -> None:
        """Update status provider berdasarkan health check"""
        config.last_health_check = datetime.utcnow()
        
        if is_healthy:
            config.status = ProviderStatus.HEALTHY
            config.error_count = 0
        else:
            config.error_count += 1
            if config.error_count >= config.max_errors:
                config.status = ProviderStatus.UNHEALTHY
    
    async def perform_health_checks(self, configs: Dict[str, ProviderConfig]) -> Dict[str, bool]:
        """Perform health checks on all providers"""
        results = {}
        
        for name, config in configs.items():
            if not config.is_active:
                results[name] = False
                continue
            
            try:
                # Create provider instance for health check
                provider = config.provider_class(**config.config)
                is_healthy = await self.check_provider_health(provider)
                await self.update_provider_status(config, is_healthy)
                results[name] = is_healthy
                
                self.logger.info(f"Health check for {name}: {'PASS' if is_healthy else 'FAIL'}")
                
            except Exception as e:
                self.logger.error(f"Error during health check for {name}: {e}")
                await self.update_provider_status(config, False)
                results[name] = False
        
        return results
    
    def get_health_summary(self, configs: Dict[str, ProviderConfig]) -> Dict:
        """Get summary of provider health status"""
        summary = {
            "total_providers": len(configs),
            "healthy": 0,
            "unhealthy": 0,
            "maintenance": 0,
            "disabled": 0,
            "providers": {}
        }
        
        for name, config in configs.items():
            status = config.status.value
            summary["providers"][name] = {
                "status": status,
                "error_count": config.error_count,
                "last_health_check": config.last_health_check.isoformat() if config.last_health_check else None,
                "is_active": config.is_active
            }
            
            # Count by status
            if status == "healthy":
                summary["healthy"] += 1
            elif status == "unhealthy":
                summary["unhealthy"] += 1
            elif status == "maintenance":
                summary["maintenance"] += 1
            elif status == "disabled":
                summary["disabled"] += 1
        
        return summary
    
    async def mark_provider_maintenance(self, config: ProviderConfig, reason: str = None) -> None:
        """Mark provider as under maintenance"""
        config.status = ProviderStatus.MAINTENANCE
        self.logger.info(f"Provider {config.name} marked as maintenance. Reason: {reason}")
    
    async def mark_provider_disabled(self, config: ProviderConfig, reason: str = None) -> None:
        """Mark provider as disabled"""
        config.status = ProviderStatus.DISABLED
        config.is_active = False
        self.logger.info(f"Provider {config.name} disabled. Reason: {reason}")
    
    async def enable_provider(self, config: ProviderConfig) -> None:
        """Enable provider and reset status"""
        config.is_active = True
        config.status = ProviderStatus.HEALTHY
        config.error_count = 0
        self.logger.info(f"Provider {config.name} enabled")

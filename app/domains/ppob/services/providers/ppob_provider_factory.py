from typing import Dict, List, Optional, Type
import logging

from app.services.ppob.base import PPOBProviderInterface
from app.services.ppob.providers.digiflazz_provider import DigiflazzProvider
from app.services.ppob.providers.default_provider import DefaultPPOBProvider

from .provider_config import ProviderConfig, ProviderStatus
from .provider_health_monitor import ProviderHealthMonitor
from .provider_load_balancer import ProviderLoadBalancer


class PPOBProviderFactory:
    """
    Factory untuk mengelola multiple PPOB provider - Factory Pattern
    Menerapkan prinsip SOLID:
    - Single Responsibility: Mengelola provider instances
    - Open/Closed: Mudah menambah provider baru
    - Liskov Substitution: Semua provider mengimplementasi interface yang sama
    - Interface Segregation: Interface yang focused
    - Dependency Inversion: Bergantung pada abstraksi
    """
    
    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}
        self.health_monitor = ProviderHealthMonitor()
        self.load_balancer = ProviderLoadBalancer()
        self.logger = logging.getLogger(__name__)
        self._setup_default_providers()
    
    def _setup_default_providers(self):
        """Setup provider default"""
        # Digiflazz Provider
        self.register_provider(
            name="digiflazz",
            provider_class=DigiflazzProvider,
            priority=1,
            config={
                "username": "",
                "api_key": "",
                "production": False
            }
        )
        
        # Default Provider (fallback)
        self.register_provider(
            name="default",
            provider_class=DefaultPPOBProvider,
            priority=99,  # Lowest priority
            config={
                "api_url": "https://api.default-ppob.com",
                "api_key": "",
                "timeout": 30
            }
        )
    
    def register_provider(
        self,
        name: str,
        provider_class: Type[PPOBProviderInterface],
        priority: int,
        config: Dict,
        is_active: bool = True
    ) -> None:
        """
        Daftarkan provider baru - Open/Closed Principle
        """
        provider_config = ProviderConfig(
            name=name,
            provider_class=provider_class,
            priority=priority,
            config=config,
            is_active=is_active
        )
        
        self.providers[name] = provider_config
        self.logger.info(f"Provider {name} registered with priority {priority}")
    
    def update_provider_config(self, name: str, config: Dict) -> bool:
        """Update konfigurasi provider"""
        if name not in self.providers:
            self.logger.error(f"Provider {name} not found")
            return False
        
        self.providers[name].config.update(config)
        self.logger.info(f"Provider {name} config updated")
        return True
    
    def enable_provider(self, name: str) -> bool:
        """Aktifkan provider"""
        if name not in self.providers:
            return False
        
        self.providers[name].is_active = True
        self.providers[name].status = ProviderStatus.HEALTHY
        self.providers[name].error_count = 0
        self.logger.info(f"Provider {name} enabled")
        return True
    
    def disable_provider(self, name: str) -> bool:
        """Nonaktifkan provider"""
        if name not in self.providers:
            return False
        
        self.providers[name].is_active = False
        self.providers[name].status = ProviderStatus.DISABLED
        self.logger.info(f"Provider {name} disabled")
        return True
    
    async def get_provider(self, strategy: str = "priority") -> Optional[PPOBProviderInterface]:
        """
        Ambil provider instance berdasarkan strategi load balancing
        """
        provider_configs = list(self.providers.values())
        selected_config = self.load_balancer.select_provider(provider_configs, strategy)
        
        if not selected_config:
            self.logger.error("No available provider found")
            return None
        
        try:
            # Create provider instance
            provider = selected_config.provider_class(**selected_config.config)
            self.logger.info(f"Selected provider: {selected_config.name}")
            return provider
        except Exception as e:
            self.logger.error(f"Error creating provider {selected_config.name}: {e}")
            # Mark provider as unhealthy
            selected_config.increment_error()
            return None
    
    async def get_provider_by_name(self, name: str) -> Optional[PPOBProviderInterface]:
        """Ambil provider instance berdasarkan nama"""
        if name not in self.providers:
            self.logger.error(f"Provider {name} not found")
            return None
        
        config = self.providers[name]
        if not config.is_available():
            self.logger.error(f"Provider {name} not available")
            return None
        
        try:
            provider = config.provider_class(**config.config)
            return provider
        except Exception as e:
            self.logger.error(f"Error creating provider {name}: {e}")
            config.increment_error()
            return None
    
    def get_provider_list(self) -> List[Dict]:
        """Ambil daftar semua provider"""
        return [config.to_dict() for config in self.providers.values()]
    
    def get_available_providers(self) -> List[str]:
        """Ambil daftar provider yang tersedia"""
        return [
            name for name, config in self.providers.items()
            if config.is_available()
        ]
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Lakukan health check untuk semua provider"""
        return await self.health_monitor.perform_health_checks(self.providers)
    
    def get_health_summary(self) -> Dict:
        """Ambil ringkasan kesehatan provider"""
        return self.health_monitor.get_health_summary(self.providers)
    
    def remove_provider(self, name: str) -> bool:
        """Hapus provider dari factory"""
        if name not in self.providers:
            return False
        
        del self.providers[name]
        self.logger.info(f"Provider {name} removed")
        return True
    
    def reset_provider_errors(self, name: str) -> bool:
        """Reset error count untuk provider"""
        if name not in self.providers:
            return False
        
        self.providers[name].reset_errors()
        self.logger.info(f"Provider {name} errors reset")
        return True
    
    def set_provider_maintenance(self, name: str, reason: str = None) -> bool:
        """Set provider ke mode maintenance"""
        if name not in self.providers:
            return False
        
        config = self.providers[name]
        config.status = ProviderStatus.MAINTENANCE
        self.logger.info(f"Provider {name} set to maintenance. Reason: {reason}")
        return True

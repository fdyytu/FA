from typing import Dict, List, Optional, Type
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime

from app.services.ppob.base import PPOBProviderInterface
from app.services.ppob.providers.digiflazz_provider import DigiflazzProvider
from app.services.ppob.providers.default_provider import DefaultPPOBProvider


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
                self.logger.warning(
                    f"Provider {config.name} marked as unhealthy after {config.error_count} errors"
                )


class ProviderLoadBalancer:
    """
    Load balancer untuk provider - Single Responsibility: Load balancing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def select_provider(
        self, 
        providers: List[ProviderConfig],
        strategy: str = "priority"
    ) -> Optional[ProviderConfig]:
        """
        Pilih provider berdasarkan strategi - Strategy Pattern
        """
        # Filter provider yang aktif dan sehat
        available_providers = [
            p for p in providers 
            if p.is_active and p.status == ProviderStatus.HEALTHY
        ]
        
        if not available_providers:
            self.logger.error("No healthy providers available")
            return None
        
        if strategy == "priority":
            return self._select_by_priority(available_providers)
        elif strategy == "round_robin":
            return self._select_round_robin(available_providers)
        elif strategy == "least_errors":
            return self._select_least_errors(available_providers)
        else:
            return available_providers[0]
    
    def _select_by_priority(self, providers: List[ProviderConfig]) -> ProviderConfig:
        """Pilih berdasarkan prioritas tertinggi"""
        return min(providers, key=lambda p: p.priority)
    
    def _select_round_robin(self, providers: List[ProviderConfig]) -> ProviderConfig:
        """Pilih berdasarkan round robin - implementasi sederhana"""
        # Implementasi round robin sederhana
        # Bisa diperluas dengan state management yang lebih kompleks
        return providers[0]
    
    def _select_least_errors(self, providers: List[ProviderConfig]) -> ProviderConfig:
        """Pilih provider dengan error paling sedikit"""
        return min(providers, key=lambda p: p.error_count)


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
            return False
        
        self.providers[name].config.update(config)
        self.logger.info(f"Provider {name} configuration updated")
        return True
    
    def enable_provider(self, name: str) -> bool:
        """Aktifkan provider"""
        if name not in self.providers:
            return False
        
        self.providers[name].is_active = True
        self.providers[name].status = ProviderStatus.HEALTHY
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
    
    async def get_provider(
        self, 
        strategy: str = "priority",
        category: Optional[str] = None
    ) -> Optional[PPOBProviderInterface]:
        """
        Ambil provider instance berdasarkan strategi - Strategy Pattern
        """
        # Filter provider berdasarkan kategori jika diperlukan
        available_providers = list(self.providers.values())
        
        if category:
            # Filter provider yang support kategori tertentu
            available_providers = [
                p for p in available_providers
                if self._provider_supports_category(p, category)
            ]
        
        # Pilih provider menggunakan load balancer
        selected_config = self.load_balancer.select_provider(
            available_providers, strategy
        )
        
        if not selected_config:
            self.logger.error("No provider available")
            return None
        
        try:
            # Buat instance provider
            provider_instance = selected_config.provider_class(
                **selected_config.config
            )
            
            self.logger.info(f"Using provider: {selected_config.name}")
            return provider_instance
            
        except Exception as e:
            self.logger.error(f"Failed to create provider instance: {e}")
            # Mark provider as unhealthy
            selected_config.status = ProviderStatus.UNHEALTHY
            selected_config.error_count += 1
            
            # Try next available provider
            return await self._get_fallback_provider(available_providers, selected_config)
    
    async def _get_fallback_provider(
        self, 
        available_providers: List[ProviderConfig],
        failed_provider: ProviderConfig
    ) -> Optional[PPOBProviderInterface]:
        """Ambil fallback provider jika provider utama gagal"""
        # Remove failed provider from list
        fallback_providers = [
            p for p in available_providers 
            if p.name != failed_provider.name and p.status == ProviderStatus.HEALTHY
        ]
        
        if not fallback_providers:
            return None
        
        # Select fallback provider
        fallback_config = self.load_balancer.select_provider(fallback_providers)
        
        if fallback_config:
            try:
                provider_instance = fallback_config.provider_class(
                    **fallback_config.config
                )
                self.logger.info(f"Using fallback provider: {fallback_config.name}")
                return provider_instance
            except Exception as e:
                self.logger.error(f"Fallback provider also failed: {e}")
        
        return None
    
    def _provider_supports_category(
        self, 
        provider_config: ProviderConfig, 
        category: str
    ) -> bool:
        """Cek apakah provider mendukung kategori tertentu"""
        # Implementasi sederhana - bisa diperluas
        # Setiap provider bisa memiliki list kategori yang didukung
        supported_categories = provider_config.config.get("supported_categories", [])
        
        if not supported_categories:
            return True  # Support all categories by default
        
        return category in supported_categories
    
    async def health_check_all_providers(self) -> Dict[str, Dict]:
        """Lakukan health check untuk semua provider"""
        results = {}
        
        for name, config in self.providers.items():
            if not config.is_active:
                results[name] = {
                    "status": "disabled",
                    "last_check": None
                }
                continue
            
            try:
                provider_instance = config.provider_class(**config.config)
                is_healthy = await self.health_monitor.check_provider_health(provider_instance)
                
                await self.health_monitor.update_provider_status(config, is_healthy)
                
                results[name] = {
                    "status": config.status.value,
                    "last_check": config.last_health_check.isoformat() if config.last_health_check else None,
                    "error_count": config.error_count,
                    "priority": config.priority
                }
                
            except Exception as e:
                self.logger.error(f"Health check failed for {name}: {e}")
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
        
        return results
    
    def get_provider_stats(self) -> Dict[str, Dict]:
        """Ambil statistik provider"""
        stats = {}
        
        for name, config in self.providers.items():
            stats[name] = {
                "name": name,
                "priority": config.priority,
                "is_active": config.is_active,
                "status": config.status.value,
                "error_count": config.error_count,
                "last_health_check": config.last_health_check.isoformat() if config.last_health_check else None
            }
        
        return stats
    
    def get_active_providers(self) -> List[str]:
        """Ambil daftar provider aktif"""
        return [
            name for name, config in self.providers.items()
            if config.is_active and config.status == ProviderStatus.HEALTHY
        ]


# Singleton instance
provider_factory = PPOBProviderFactory()

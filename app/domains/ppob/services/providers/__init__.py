"""
PPOB Provider modules yang telah dipecah menjadi beberapa file terpisah
untuk meningkatkan maintainability dan mengikuti prinsip Single Responsibility.
"""

from .provider_config import ProviderConfig, ProviderStatus
from .provider_health_monitor import ProviderHealthMonitor
from .provider_load_balancer import ProviderLoadBalancer
from .ppob_provider_factory import PPOBProviderFactory

__all__ = [
    'ProviderConfig',
    'ProviderStatus',
    'ProviderHealthMonitor',
    'ProviderLoadBalancer',
    'PPOBProviderFactory'
]

# Dokumentasi untuk setiap komponen:

# ProviderConfig & ProviderStatus
# - Mengelola konfigurasi dan status provider
# - Enum untuk status provider (HEALTHY, UNHEALTHY, MAINTENANCE, DISABLED)

# ProviderHealthMonitor
# - Melakukan health check pada provider
# - Monitoring kesehatan dan update status provider

# ProviderLoadBalancer
# - Implementasi load balancing strategies
# - Strategy pattern untuk pemilihan provider (priority, round_robin, least_errors, random)

# PPOBProviderFactory
# - Factory pattern untuk mengelola multiple provider
# - Orchestration semua komponen provider

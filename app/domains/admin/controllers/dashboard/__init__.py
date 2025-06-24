"""
Dashboard controllers package
Memecah dashboard controller menjadi modul-modul kecil
"""

from .dashboard_main_controller import DashboardMainController
from .dashboard_stats_controller import DashboardStatsController
from .dashboard_system_controller import DashboardSystemController

__all__ = [
    'DashboardMainController',
    'DashboardStatsController',
    'DashboardSystemController'
]

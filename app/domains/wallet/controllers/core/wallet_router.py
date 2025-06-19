"""
Modul ini berisi setup router utama untuk Wallet controllers.
"""

from fastapi import APIRouter
from app.domains.wallet.controllers.wallet_balance_controller import WalletBalanceController
from app.domains.wallet.controllers.wallet_transaction_controller import WalletTransactionController
from app.domains.wallet.controllers.wallet_topup_controller import WalletTopUpController
from app.domains.wallet.controllers.wallet_admin_controller import WalletAdminController

class WalletRouter:
    """
    Router utama yang mengintegrasikan semua sub-controller wallet.
    Mengimplementasikan Single Responsibility Principle dengan memisahkan logika ke sub-controller.
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/wallet", tags=["Wallet"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup semua routes wallet dengan mengintegrasikan sub-controller"""
        # Balance routes
        balance_controller = WalletBalanceController()
        self.router.include_router(balance_controller.router)
        
        # Transaction routes
        transaction_controller = WalletTransactionController()
        self.router.include_router(transaction_controller.router)
        
        # Top-up routes
        topup_controller = WalletTopUpController()
        self.router.include_router(topup_controller.router)
        
        # Admin routes
        admin_controller = WalletAdminController()
        self.router.include_router(admin_controller.router, prefix="/admin")

# Instance router
wallet_router = WalletRouter()
main_router = wallet_router.router

__all__ = ['main_router']

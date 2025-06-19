from app.common.base_classes.base_service import BaseService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.services.wallet_transaction_service import WalletTransactionService
from app.domains.wallet.services.wallet_transfer_service import WalletTransferService
from app.domains.wallet.services.wallet_topup_service import WalletTopUpService
from app.domains.wallet.services.wallet_admin_service import WalletAdminService

class WalletService(BaseService):
    """
    Service utama untuk wallet yang mengintegrasikan semua sub-service.
    Mengimplementasikan Facade Pattern untuk menyederhanakan interface ke subsystem.
    """
    
    def __init__(self, repository: WalletRepository):
        super().__init__(repository)
        # Initialize sub-services
        self.transaction_service = WalletTransactionService(repository)
        self.transfer_service = WalletTransferService(repository)
        self.topup_service = WalletTopUpService(repository)
        self.admin_service = WalletAdminService(repository)
    
    # Delegate methods to appropriate sub-services
    
    # Transaction methods
    def get_user_balance(self, user_id: int):
        return self.transaction_service.get_user_balance(user_id)
    
    def get_transaction_history(self, *args, **kwargs):
        return self.transaction_service.get_transaction_history(*args, **kwargs)
    
    def get_wallet_stats(self, *args, **kwargs):
        return self.transaction_service.get_wallet_stats(*args, **kwargs)
    
    def get_monthly_transaction_summary(self, *args, **kwargs):
        return self.transaction_service.get_monthly_transaction_summary(*args, **kwargs)
    
    # Transfer methods
    def transfer_money(self, *args, **kwargs):
        return self.transfer_service.transfer_money(*args, **kwargs)
    
    # Top-up methods
    def create_manual_topup_request(self, *args, **kwargs):
        return self.topup_service.create_manual_topup_request(*args, **kwargs)
    
    def upload_topup_proof(self, *args, **kwargs):
        return self.topup_service.upload_topup_proof(*args, **kwargs)
    
    def create_midtrans_topup(self, *args, **kwargs):
        return self.topup_service.create_midtrans_topup(*args, **kwargs)
    
    def process_midtrans_notification(self, *args, **kwargs):
        return self.topup_service.process_midtrans_notification(*args, **kwargs)
    
    # Admin methods
    def get_pending_topup_requests(self, *args, **kwargs):
        return self.admin_service.get_pending_topup_requests(*args, **kwargs)
    
    def process_topup_approval(self, *args, **kwargs):
        return self.admin_service.process_topup_approval(*args, **kwargs)

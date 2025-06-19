from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from decimal import Decimal

from app.common.base_classes.base_service import BaseService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.models.wallet import (
    WalletTransaction, TransactionType, TransactionStatus
)
from app.common.exceptions.custom_exceptions import InsufficientBalanceError

class WalletTransactionService(BaseService):
    """Service untuk menangani transaksi dasar wallet"""
    
    def __init__(self, repository: WalletRepository):
        super().__init__(repository)
    
    def get_user_balance(self, user_id: int) -> Decimal:
        """Ambil saldo user saat ini"""
        return self.repository.get_user_balance(user_id)
    
    def create_transaction(
        self,
        user_id: int,
        transaction_type: TransactionType,
        amount: Decimal,
        description: str = None,
        reference_id: str = None,
        meta_data: str = None
    ) -> WalletTransaction:
        """Buat transaksi wallet baru"""
        try:
            # Validasi saldo untuk transaksi debit
            if transaction_type in [TransactionType.TRANSFER_SEND, TransactionType.PPOB_PAYMENT]:
                current_balance = self.get_user_balance(user_id)
                if current_balance < amount:
                    raise InsufficientBalanceError("Saldo tidak mencukupi")
            
            return self.repository.create_transaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                reference_id=reference_id,
                meta_data=meta_data
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat transaksi: {str(e)}"
            )
    
    def update_transaction_status(
        self,
        transaction_id: int,
        status: TransactionStatus,
        description: str = None
    ) -> Optional[WalletTransaction]:
        """Update status transaksi"""
        return self.repository.update_transaction_status(
            transaction_id=transaction_id,
            status=status,
            description=description
        )
    
    def get_transaction_history(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        transaction_type: Optional[TransactionType] = None
    ) -> Dict[str, Any]:
        """Ambil riwayat transaksi user"""
        try:
            skip = (page - 1) * per_page
            
            transactions = self.repository.get_user_transactions(
                user_id=user_id,
                skip=skip,
                limit=per_page,
                transaction_type=transaction_type
            )
            
            total_count = self.repository.count_user_transactions(
                user_id=user_id,
                transaction_type=transaction_type
            )
            
            total_pages = (total_count + per_page - 1) // per_page
            
            return {
                "transactions": transactions,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil riwayat transaksi: {str(e)}"
            )
    
    def get_wallet_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Ambil statistik wallet"""
        return self.repository.get_wallet_stats(user_id)
    
    def get_monthly_transaction_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Ambil ringkasan transaksi bulanan"""
        return self.repository.get_monthly_transaction_summary(year, month)

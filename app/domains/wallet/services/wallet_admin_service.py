from typing import Dict, Any
from fastapi import HTTPException, status
from datetime import datetime

from app.common.base_classes.base_service import BaseService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.models.wallet import (
    TopUpRequest, TransactionType, TransactionStatus, TopUpStatus
)
from app.domains.wallet.schemas.wallet_schemas import TopUpApprovalRequest
from app.common.exceptions.custom_exceptions import ValidationException, NotFoundError
from app.domains.wallet.services.wallet_transaction_service import WalletTransactionService

class WalletAdminService(BaseService):
    """Service untuk menangani operasi admin terkait wallet"""
    
    def __init__(self, repository: WalletRepository):
        super().__init__(repository)
        self.transaction_service = WalletTransactionService(repository)
    
    def get_pending_topup_requests(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Ambil daftar permintaan top up yang pending (Admin)"""
        try:
            skip = (page - 1) * per_page
            
            requests = self.repository.get_pending_topup_requests(skip=skip, limit=per_page)
            total_count = self.repository.count_pending_topup_requests()
            
            return {
                "requests": requests,
                "total_count": total_count,
                "page": page,
                "per_page": per_page
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil daftar permintaan top up: {str(e)}"
            )
    
    def process_topup_approval(
        self,
        request_id: int,
        approval_request: TopUpApprovalRequest,
        admin_user_id: int
    ) -> TopUpRequest:
        """Proses approval/rejection top up (Admin)"""
        try:
            # Ambil topup request
            topup_request = self.repository.get_by_id(request_id)
            if not topup_request:
                raise NotFoundError("Permintaan top up tidak ditemukan")
            
            if topup_request.status != TopUpStatus.PENDING:
                raise ValidationException("Permintaan top up sudah diproses")
            
            # Update status
            update_data = {
                "status": approval_request.status,
                "admin_notes": approval_request.admin_notes,
                "processed_by": admin_user_id,
                "processed_at": datetime.utcnow()
            }
            
            # Jika approved, buat transaksi wallet
            if approval_request.status == TopUpStatus.APPROVED:
                transaction = self.transaction_service.create_transaction(
                    user_id=topup_request.user_id,
                    transaction_type=TransactionType.TOPUP_MANUAL,
                    amount=topup_request.amount,
                    description="Top up manual - Approved by admin",
                    reference_id=topup_request.request_code
                )
                
                # Update status transaksi menjadi success
                self.transaction_service.update_transaction_status(
                    transaction.id, 
                    TransactionStatus.SUCCESS
                )
                
                # Update topup request dengan wallet transaction ID
                update_data["wallet_transaction_id"] = transaction.id
            
            return self.repository.update_topup_request(request_id, update_data)
            
        except (ValidationException, NotFoundError):
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memproses approval: {str(e)}"
            )

from typing import Dict, Any
from fastapi import HTTPException, status
from datetime import datetime

from app.common.base_classes.base_service import BaseService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.models.wallet import (
    TopUpRequest, TransactionType, TransactionStatus,
    PaymentMethod, TopUpStatus
)
from app.domains.wallet.schemas.wallet_schemas import (
    TopUpManualRequest, TopUpMidtransRequest, TopUpApprovalRequest
)
from app.domains.auth.models.user import User
from app.common.exceptions.custom_exceptions import ValidationException, NotFoundError
from app.domains.wallet.services.wallet_transaction_service import WalletTransactionService

class WalletTopUpService(BaseService):
    """Service untuk menangani top-up wallet"""
    
    def __init__(self, repository: WalletRepository):
        super().__init__(repository)
        self.transaction_service = WalletTransactionService(repository)
    
    def create_manual_topup_request(
        self,
        user_id: int,
        topup_request: TopUpManualRequest
    ) -> TopUpRequest:
        """Buat permintaan top up manual"""
        try:
            return self.repository.create_topup_request(
                user_id=user_id,
                amount=topup_request.amount,
                payment_method=topup_request.payment_method,
                bank_name=topup_request.bank_name,
                account_number=topup_request.account_number,
                account_name=topup_request.account_name,
                notes=topup_request.notes
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat permintaan top up: {str(e)}"
            )
    
    def upload_topup_proof(
        self,
        request_id: int,
        user_id: int,
        proof_image_path: str
    ) -> TopUpRequest:
        """Upload bukti pembayaran top up"""
        try:
            # Validasi request milik user
            topup_request = self.repository.get_by_id(request_id)
            if not topup_request or topup_request.user_id != user_id:
                raise NotFoundError("Permintaan top up tidak ditemukan")
            
            if topup_request.status != TopUpStatus.PENDING:
                raise ValidationException("Permintaan top up sudah diproses")
            
            # Update dengan bukti pembayaran
            update_data = {
                "proof_image": proof_image_path,
                "updated_at": datetime.utcnow()
            }
            
            return self.repository.update_topup_request(request_id, update_data)
            
        except (ValidationException, NotFoundError):
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal upload bukti pembayaran: {str(e)}"
            )
    
    def create_midtrans_topup(
        self,
        user_id: int,
        topup_request: TopUpMidtransRequest
    ) -> Dict[str, Any]:
        """Buat pembayaran top up via Midtrans"""
        try:
            # Buat topup request
            topup = self.repository.create_topup_request(
                user_id=user_id,
                amount=topup_request.amount,
                payment_method=PaymentMethod.MIDTRANS
            )
            
            # Buat pembayaran Midtrans
            user = self.repository.db.query(User).filter(User.id == user_id).first()
            
            payment_data = {
                "order_id": topup.request_code,
                "gross_amount": int(topup_request.amount),
                "customer_details": {
                    "first_name": user.full_name or user.username,
                    "email": user.email,
                    "phone": user.phone or "08123456789"
                },
                "item_details": [{
                    "id": "topup",
                    "price": int(topup_request.amount),
                    "quantity": 1,
                    "name": "Top Up Wallet"
                }]
            }
            
            midtrans_response = self.midtrans_service.create_transaction(payment_data)
            
            # Update topup request dengan data Midtrans
            update_data = {
                "midtrans_order_id": topup.request_code,
                "midtrans_transaction_id": midtrans_response.get("transaction_id"),
                "updated_at": datetime.utcnow()
            }
            
            self.repository.update_topup_request(topup.id, update_data)
            
            return {
                "request_code": topup.request_code,
                "amount": topup_request.amount,
                "midtrans_order_id": topup.request_code,
                "payment_url": midtrans_response.get("redirect_url"),
                "status": TopUpStatus.PENDING
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat pembayaran Midtrans: {str(e)}"
            )
    
    def process_midtrans_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proses notifikasi dari Midtrans"""
        try:
            order_id = notification_data.get("order_id")
            transaction_status = notification_data.get("transaction_status")
            
            # Validasi signature
            if not self.midtrans_service.verify_signature(notification_data):
                return {"success": False, "error": "Invalid signature"}
            
            # Cari topup request
            topup_request = self.repository.get_topup_request_by_code(order_id)
            if not topup_request:
                return {"success": False, "error": "Topup request not found"}
            
            # Proses berdasarkan status
            if transaction_status == "settlement":
                # Pembayaran berhasil
                self.repository.update_topup_request(topup_request.id, {
                    "status": TopUpStatus.APPROVED,
                    "processed_at": datetime.utcnow()
                })
                
                # Buat transaksi wallet
                transaction = self.transaction_service.create_transaction(
                    user_id=topup_request.user_id,
                    transaction_type=TransactionType.TOPUP_MIDTRANS,
                    amount=topup_request.amount,
                    description="Top up via Midtrans",
                    reference_id=order_id
                )
                
                # Update status transaksi menjadi success
                self.transaction_service.update_transaction_status(
                    transaction.id, 
                    TransactionStatus.SUCCESS
                )
                
                # Update topup request dengan wallet transaction ID
                self.repository.update_topup_request(topup_request.id, {
                    "wallet_transaction_id": transaction.id
                })
                
                return {"success": True, "message": "Payment processed successfully"}
                
            elif transaction_status in ["cancel", "deny", "expire"]:
                # Pembayaran gagal
                self.repository.update_topup_request(topup_request.id, {
                    "status": TopUpStatus.REJECTED,
                    "processed_at": datetime.utcnow(),
                    "admin_notes": f"Payment {transaction_status}"
                })
                
                return {"success": True, "message": "Payment cancelled"}
            
            return {"success": True, "message": "Notification processed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

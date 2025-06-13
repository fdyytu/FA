from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import datetime

from app.shared.base_classes.base_service import BaseService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.models.wallet import (
    WalletTransaction, Transfer, TopUpRequest,
    TransactionType, TransactionStatus, PaymentMethod, TopUpStatus
)
from app.domains.wallet.schemas.wallet_schemas import (
    WalletTransactionCreate, WalletTransactionUpdate, TransferRequest,
    TopUpManualRequest, TopUpMidtransRequest, TopUpApprovalRequest
)
from app.models.user import User
from app.services.midtrans_service import MidtransService
from app.utils.exceptions import ValidationError, NotFoundError, InsufficientBalanceError

class WalletService(BaseService[WalletTransaction, WalletRepository, WalletTransactionCreate, WalletTransactionUpdate]):
    """
    Service untuk menangani transaksi wallet.
    Mengimplementasikan Single Responsibility Principle - hanya menangani logika bisnis wallet.
    """
    
    def __init__(self, repository: WalletRepository):
        super().__init__(repository)
        self.midtrans_service = MidtransService()
    
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
    
    def transfer_money(self, sender_id: int, transfer_request: TransferRequest) -> Transfer:
        """Transfer uang antar user"""
        try:
            # Validasi receiver
            receiver = self.repository.db.query(User).filter(
                User.username == transfer_request.receiver_username
            ).first()
            
            if not receiver:
                raise NotFoundError("User penerima tidak ditemukan")
            
            if receiver.id == sender_id:
                raise ValidationError("Tidak dapat transfer ke diri sendiri")
            
            # Validasi saldo sender
            sender_balance = self.get_user_balance(sender_id)
            if sender_balance < transfer_request.amount:
                raise InsufficientBalanceError("Saldo tidak mencukupi")
            
            # Buat transfer record
            transfer = self.repository.create_transfer(
                sender_id=sender_id,
                receiver_id=receiver.id,
                amount=transfer_request.amount,
                description=transfer_request.description
            )
            
            # Buat transaksi untuk sender (debit)
            sender_transaction = self.create_transaction(
                user_id=sender_id,
                transaction_type=TransactionType.TRANSFER_SEND,
                amount=transfer_request.amount,
                description=f"Transfer ke {receiver.username}",
                reference_id=transfer.transfer_code
            )
            
            # Ambil data sender
            sender = self.repository.db.query(User).filter(User.id == sender_id).first()
            
            # Buat transaksi untuk receiver (credit)
            receiver_transaction = self.create_transaction(
                user_id=receiver.id,
                transaction_type=TransactionType.TRANSFER_RECEIVE,
                amount=transfer_request.amount,
                description=f"Transfer dari {sender.username}",
                reference_id=transfer.transfer_code
            )
            
            # Update status transaksi menjadi success
            self.update_transaction_status(sender_transaction.id, TransactionStatus.SUCCESS)
            self.update_transaction_status(receiver_transaction.id, TransactionStatus.SUCCESS)
            
            # Update transfer dengan transaction IDs
            self.repository.update_transfer_status(
                transfer_id=transfer.id,
                status=TransactionStatus.SUCCESS,
                sender_transaction_id=sender_transaction.id,
                receiver_transaction_id=receiver_transaction.id
            )
            
            return transfer
            
        except (ValidationError, NotFoundError, InsufficientBalanceError):
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal melakukan transfer: {str(e)}"
            )
    
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
                raise ValidationError("Permintaan top up sudah diproses")
            
            # Update dengan bukti pembayaran
            update_data = {
                "proof_image": proof_image_path,
                "updated_at": datetime.utcnow()
            }
            
            return self.repository.update_topup_request(request_id, update_data)
            
        except (ValidationError, NotFoundError):
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
                transaction = self.create_transaction(
                    user_id=topup_request.user_id,
                    transaction_type=TransactionType.TOPUP_MIDTRANS,
                    amount=topup_request.amount,
                    description="Top up via Midtrans",
                    reference_id=order_id
                )
                
                # Update status transaksi menjadi success
                self.update_transaction_status(transaction.id, TransactionStatus.SUCCESS)
                
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
                raise ValidationError("Permintaan top up sudah diproses")
            
            # Update status
            update_data = {
                "status": approval_request.status,
                "admin_notes": approval_request.admin_notes,
                "processed_by": admin_user_id,
                "processed_at": datetime.utcnow()
            }
            
            # Jika approved, buat transaksi wallet
            if approval_request.status == TopUpStatus.APPROVED:
                transaction = self.create_transaction(
                    user_id=topup_request.user_id,
                    transaction_type=TransactionType.TOPUP_MANUAL,
                    amount=topup_request.amount,
                    description="Top up manual - Approved by admin",
                    reference_id=topup_request.request_code
                )
                
                # Update status transaksi menjadi success
                self.update_transaction_status(transaction.id, TransactionStatus.SUCCESS)
                
                # Update topup request dengan wallet transaction ID
                update_data["wallet_transaction_id"] = transaction.id
            
            return self.repository.update_topup_request(request_id, update_data)
            
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memproses approval: {str(e)}"
            )
    
    def get_wallet_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Ambil statistik wallet"""
        return self.repository.get_wallet_stats(user_id)
    
    def get_monthly_transaction_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Ambil ringkasan transaksi bulanan"""
        return self.repository.get_monthly_transaction_summary(year, month)

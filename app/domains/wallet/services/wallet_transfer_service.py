from fastapi import HTTPException, status
from decimal import Decimal

from app.common.base_classes.base_service import BaseService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.models.wallet import (
    Transfer, TransactionType, TransactionStatus
)
from app.domains.wallet.schemas.wallet_schemas import TransferRequest
from app.domains.auth.models.user import User
from app.common.exceptions.custom_exceptions import (
    ValidationException, NotFoundError, InsufficientBalanceError
)
from app.domains.wallet.services.wallet_transaction_service import WalletTransactionService

class WalletTransferService(BaseService):
    """Service untuk menangani transfer antar user"""
    
    def __init__(self, repository: WalletRepository):
        super().__init__(repository)
        self.transaction_service = WalletTransactionService(repository)
    
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
                raise ValidationException("Tidak dapat transfer ke diri sendiri")
            
            # Validasi saldo sender
            sender_balance = self.transaction_service.get_user_balance(sender_id)
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
            sender_transaction = self.transaction_service.create_transaction(
                user_id=sender_id,
                transaction_type=TransactionType.TRANSFER_SEND,
                amount=transfer_request.amount,
                description=f"Transfer ke {receiver.username}",
                reference_id=transfer.transfer_code
            )
            
            # Ambil data sender
            sender = self.repository.db.query(User).filter(User.id == sender_id).first()
            
            # Buat transaksi untuk receiver (credit)
            receiver_transaction = self.transaction_service.create_transaction(
                user_id=receiver.id,
                transaction_type=TransactionType.TRANSFER_RECEIVE,
                amount=transfer_request.amount,
                description=f"Transfer dari {sender.username}",
                reference_id=transfer.transfer_code
            )
            
            # Update status transaksi menjadi success
            self.transaction_service.update_transaction_status(
                sender_transaction.id, 
                TransactionStatus.SUCCESS
            )
            self.transaction_service.update_transaction_status(
                receiver_transaction.id, 
                TransactionStatus.SUCCESS
            )
            
            # Update transfer dengan transaction IDs
            self.repository.update_transfer_status(
                transfer_id=transfer.id,
                status=TransactionStatus.SUCCESS,
                sender_transaction_id=sender_transaction.id,
                receiver_transaction_id=receiver_transaction.id
            )
            
            return transfer
            
        except (ValidationException, NotFoundError, InsufficientBalanceError):
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal melakukan transfer: {str(e)}"
            )

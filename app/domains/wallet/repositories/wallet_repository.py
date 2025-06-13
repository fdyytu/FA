from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from app.shared.base_classes.base_repository import BaseRepository
from app.domains.wallet.models.wallet import (
    WalletTransaction, Transfer, TopUpRequest, 
    TransactionType, TransactionStatus, TopUpStatus, PaymentMethod
)

class WalletRepository(BaseRepository[WalletTransaction, dict, dict]):
    """
    Repository untuk Wallet yang mengimplementasikan Repository Pattern.
    Menangani semua operasi database terkait wallet dan transaksi keuangan.
    """
    
    def __init__(self, db: Session):
        super().__init__(db, WalletTransaction)
    
    def get_user_balance(self, user_id: int) -> Decimal:
        """Ambil saldo user saat ini"""
        last_transaction = self.db.query(WalletTransaction).filter(
            WalletTransaction.user_id == user_id,
            WalletTransaction.status == TransactionStatus.SUCCESS
        ).order_by(desc(WalletTransaction.created_at)).first()
        
        if last_transaction:
            return last_transaction.balance_after
        return Decimal('0')
    
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
        # Ambil saldo sebelumnya
        balance_before = self.get_user_balance(user_id)
        
        # Hitung saldo setelah transaksi
        if transaction_type in [TransactionType.TOPUP_MANUAL, TransactionType.TOPUP_MIDTRANS, 
                               TransactionType.TRANSFER_RECEIVE, TransactionType.REFUND]:
            balance_after = balance_before + amount
        else:
            balance_after = balance_before - amount
        
        # Generate transaction code
        transaction_code = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"
        
        transaction = WalletTransaction(
            user_id=user_id,
            transaction_code=transaction_code,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status=TransactionStatus.PENDING,
            description=description,
            reference_id=reference_id,
            meta_data=meta_data
        )
        
        return self.create(transaction)
    
    def update_transaction_status(
        self, 
        transaction_id: int, 
        status: TransactionStatus,
        description: str = None
    ) -> Optional[WalletTransaction]:
        """Update status transaksi"""
        update_data = {"status": status}
        if description:
            update_data["description"] = description
        
        return self.update(transaction_id, update_data)
    
    def get_user_transactions(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> List[WalletTransaction]:
        """Ambil transaksi user dengan filter"""
        query = self.db.query(WalletTransaction).filter(
            WalletTransaction.user_id == user_id
        )
        
        if transaction_type:
            query = query.filter(WalletTransaction.transaction_type == transaction_type)
        
        if status:
            query = query.filter(WalletTransaction.status == status)
        
        return query.order_by(desc(WalletTransaction.created_at)).offset(skip).limit(limit).all()
    
    def count_user_transactions(
        self, 
        user_id: int,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> int:
        """Hitung total transaksi user"""
        query = self.db.query(WalletTransaction).filter(
            WalletTransaction.user_id == user_id
        )
        
        if transaction_type:
            query = query.filter(WalletTransaction.transaction_type == transaction_type)
        
        if status:
            query = query.filter(WalletTransaction.status == status)
        
        return query.count()
    
    # Transfer methods
    def create_transfer(
        self,
        sender_id: int,
        receiver_id: int,
        amount: Decimal,
        description: str = None
    ) -> Transfer:
        """Buat transfer baru"""
        transfer_code = f"TRF{datetime.now().strftime('%Y%m%d%H%M%S')}{sender_id}"
        
        transfer = Transfer(
            sender_id=sender_id,
            receiver_id=receiver_id,
            transfer_code=transfer_code,
            amount=amount,
            status=TransactionStatus.PENDING,
            description=description
        )
        
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        return transfer
    
    def update_transfer_status(
        self, 
        transfer_id: int, 
        status: TransactionStatus,
        sender_transaction_id: int = None,
        receiver_transaction_id: int = None
    ) -> Optional[Transfer]:
        """Update status transfer"""
        transfer = self.db.query(Transfer).filter(Transfer.id == transfer_id).first()
        if transfer:
            transfer.status = status
            if sender_transaction_id:
                transfer.sender_transaction_id = sender_transaction_id
            if receiver_transaction_id:
                transfer.receiver_transaction_id = receiver_transaction_id
            
            self.db.commit()
            self.db.refresh(transfer)
        return transfer
    
    def get_transfer_by_code(self, transfer_code: str) -> Optional[Transfer]:
        """Ambil transfer berdasarkan kode"""
        return self.db.query(Transfer).filter(Transfer.transfer_code == transfer_code).first()
    
    # TopUp methods
    def create_topup_request(
        self,
        user_id: int,
        amount: Decimal,
        payment_method: PaymentMethod,
        bank_name: str = None,
        account_number: str = None,
        account_name: str = None,
        notes: str = None
    ) -> TopUpRequest:
        """Buat permintaan top up baru"""
        request_code = f"TOP{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"
        
        topup_request = TopUpRequest(
            user_id=user_id,
            request_code=request_code,
            amount=amount,
            payment_method=payment_method,
            status=TopUpStatus.PENDING,
            bank_name=bank_name,
            account_number=account_number,
            account_name=account_name,
            notes=notes
        )
        
        self.db.add(topup_request)
        self.db.commit()
        self.db.refresh(topup_request)
        return topup_request
    
    def update_topup_request(
        self, 
        request_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[TopUpRequest]:
        """Update permintaan top up"""
        topup_request = self.db.query(TopUpRequest).filter(TopUpRequest.id == request_id).first()
        if topup_request:
            for key, value in update_data.items():
                setattr(topup_request, key, value)
            
            self.db.commit()
            self.db.refresh(topup_request)
        return topup_request
    
    def get_topup_request_by_code(self, request_code: str) -> Optional[TopUpRequest]:
        """Ambil permintaan top up berdasarkan kode"""
        return self.db.query(TopUpRequest).filter(TopUpRequest.request_code == request_code).first()
    
    def get_pending_topup_requests(self, skip: int = 0, limit: int = 10) -> List[TopUpRequest]:
        """Ambil permintaan top up yang pending"""
        return self.db.query(TopUpRequest).filter(
            TopUpRequest.status == TopUpStatus.PENDING
        ).order_by(desc(TopUpRequest.created_at)).offset(skip).limit(limit).all()
    
    def count_pending_topup_requests(self) -> int:
        """Hitung total permintaan top up yang pending"""
        return self.db.query(TopUpRequest).filter(
            TopUpRequest.status == TopUpStatus.PENDING
        ).count()
    
    def get_user_topup_requests(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10,
        status: Optional[TopUpStatus] = None
    ) -> List[TopUpRequest]:
        """Ambil permintaan top up user"""
        query = self.db.query(TopUpRequest).filter(TopUpRequest.user_id == user_id)
        
        if status:
            query = query.filter(TopUpRequest.status == status)
        
        return query.order_by(desc(TopUpRequest.created_at)).offset(skip).limit(limit).all()
    
    # Statistics methods
    def get_wallet_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Ambil statistik wallet"""
        query = self.db.query(WalletTransaction)
        
        if user_id:
            query = query.filter(WalletTransaction.user_id == user_id)
        
        # Total transaksi
        total_transactions = query.count()
        
        # Transaksi berhasil
        success_transactions = query.filter(
            WalletTransaction.status == TransactionStatus.SUCCESS
        ).count()
        
        # Total top up
        total_topup = query.filter(
            WalletTransaction.transaction_type.in_([
                TransactionType.TOPUP_MANUAL, 
                TransactionType.TOPUP_MIDTRANS
            ]),
            WalletTransaction.status == TransactionStatus.SUCCESS
        ).with_entities(func.sum(WalletTransaction.amount)).scalar() or 0
        
        # Total transfer keluar
        total_transfer_out = query.filter(
            WalletTransaction.transaction_type == TransactionType.TRANSFER_SEND,
            WalletTransaction.status == TransactionStatus.SUCCESS
        ).with_entities(func.sum(WalletTransaction.amount)).scalar() or 0
        
        # Transaksi hari ini
        today = datetime.utcnow().date()
        today_transactions = query.filter(
            func.date(WalletTransaction.created_at) == today
        ).count()
        
        return {
            "total_transactions": total_transactions,
            "success_transactions": success_transactions,
            "failed_transactions": query.filter(
                WalletTransaction.status == TransactionStatus.FAILED
            ).count(),
            "pending_transactions": query.filter(
                WalletTransaction.status == TransactionStatus.PENDING
            ).count(),
            "total_topup": float(total_topup),
            "total_transfer_out": float(total_transfer_out),
            "today_transactions": today_transactions,
            "success_rate": (success_transactions / total_transactions * 100) if total_transactions > 0 else 0
        }
    
    def get_monthly_transaction_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Ambil ringkasan transaksi bulanan"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        query = self.db.query(WalletTransaction).filter(
            WalletTransaction.status == TransactionStatus.SUCCESS,
            WalletTransaction.created_at >= start_date,
            WalletTransaction.created_at < end_date
        )
        
        # Total per tipe transaksi
        topup_total = query.filter(
            WalletTransaction.transaction_type.in_([
                TransactionType.TOPUP_MANUAL, 
                TransactionType.TOPUP_MIDTRANS
            ])
        ).with_entities(func.sum(WalletTransaction.amount)).scalar() or 0
        
        transfer_total = query.filter(
            WalletTransaction.transaction_type == TransactionType.TRANSFER_SEND
        ).with_entities(func.sum(WalletTransaction.amount)).scalar() or 0
        
        ppob_total = query.filter(
            WalletTransaction.transaction_type == TransactionType.PPOB_PAYMENT
        ).with_entities(func.sum(WalletTransaction.amount)).scalar() or 0
        
        return {
            "year": year,
            "month": month,
            "total_topup": float(topup_total),
            "total_transfer": float(transfer_total),
            "total_ppob": float(ppob_total),
            "total_transactions": query.count()
        }

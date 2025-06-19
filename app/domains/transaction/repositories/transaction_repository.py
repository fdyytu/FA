from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from app.domains.transaction.models.transaction import Transaction, TransactionLog, TransactionStatus, TransactionType
from app.domains.transaction.schemas.transaction_schemas import TransactionCreate, TransactionUpdate
from app.shared.base_classes.base_repository import BaseRepository
import uuid
import json

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(Transaction, db)
    
    def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:
        """Create a new transaction with auto-generated transaction ID"""
        # Generate unique transaction ID
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        # Calculate total amount
        total_amount = transaction_data.amount + (transaction_data.fee or 0)
        
        # Prepare extra_data
        extra_data_str = None
        if transaction_data.extra_data:
            extra_data_str = json.dumps(transaction_data.extra_data)
        
        db_transaction = Transaction(
            transaction_id=transaction_id,
            user_id=transaction_data.user_id,
            transaction_type=transaction_data.transaction_type,
            amount=transaction_data.amount,
            fee=transaction_data.fee or 0,
            total_amount=total_amount,
            description=transaction_data.description,
            reference_id=transaction_data.reference_id,
            payment_method=transaction_data.payment_method,
            extra_data=extra_data_str,
            notes=transaction_data.notes
        )
        
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        
        # Create initial log
        self.add_transaction_log(
            transaction_id=transaction_id,
            status_to=TransactionStatus.PENDING,
            message="Transaction created"
        )
        
        return db_transaction
    
    def update_transaction_status(self, transaction_id: str, status: TransactionStatus, message: Optional[str] = None) -> Optional[Transaction]:
        """Update transaction status and create log entry"""
        transaction = self.get_by_transaction_id(transaction_id)
        if not transaction:
            return None
        
        old_status = transaction.status
        transaction.status = status
        
        if status in [TransactionStatus.SUCCESS, TransactionStatus.FAILED, TransactionStatus.CANCELLED]:
            transaction.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        
        # Create log entry
        self.add_transaction_log(
            transaction_id=transaction_id,
            status_from=old_status,
            status_to=status,
            message=message or f"Status updated to {status.value}"
        )
        
        return transaction
    
    def get_by_transaction_id(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by transaction ID"""
        return self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get transactions by user ID"""
        return (
            self.db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(desc(Transaction.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(self, status: TransactionStatus, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get transactions by status"""
        return (
            self.db.query(Transaction)
            .filter(Transaction.status == status)
            .order_by(desc(Transaction.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_type(self, transaction_type: TransactionType, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get transactions by type"""
        return (
            self.db.query(Transaction)
            .filter(Transaction.transaction_type == transaction_type)
            .order_by(desc(Transaction.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get transactions within date range"""
        return (
            self.db.query(Transaction)
            .filter(and_(
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            ))
            .order_by(desc(Transaction.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_transaction_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get transaction statistics"""
        query = self.db.query(Transaction)
        
        if start_date and end_date:
            query = query.filter(and_(
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            ))
        
        total_transactions = query.count()
        total_amount = query.with_entities(func.sum(Transaction.total_amount)).scalar() or 0
        successful_transactions = query.filter(Transaction.status == TransactionStatus.SUCCESS).count()
        failed_transactions = query.filter(Transaction.status == TransactionStatus.FAILED).count()
        pending_transactions = query.filter(Transaction.status == TransactionStatus.PENDING).count()
        
        return {
            "total_transactions": total_transactions,
            "total_amount": total_amount,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "pending_transactions": pending_transactions
        }
    
    def add_transaction_log(self, transaction_id: str, status_to: TransactionStatus, status_from: Optional[TransactionStatus] = None, message: Optional[str] = None):
        """Add transaction log entry"""
        log_entry = TransactionLog(
            transaction_id=transaction_id,
            status_from=status_from,
            status_to=status_to,
            message=message
        )
        
        self.db.add(log_entry)
        self.db.commit()
    
    def get_transaction_logs(self, transaction_id: str) -> List[TransactionLog]:
        """Get all logs for a transaction"""
        return (
            self.db.query(TransactionLog)
            .filter(TransactionLog.transaction_id == transaction_id)
            .order_by(TransactionLog.created_at)
            .all()
        )
    
    def search_transactions(self, 
                          user_id: Optional[int] = None,
                          status: Optional[TransactionStatus] = None,
                          transaction_type: Optional[TransactionType] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          search_term: Optional[str] = None,
                          skip: int = 0,
                          limit: int = 100) -> List[Transaction]:
        """Search transactions with multiple filters"""
        query = self.db.query(Transaction)
        
        if user_id:
            query = query.filter(Transaction.user_id == user_id)
        
        if status:
            query = query.filter(Transaction.status == status)
        
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        if start_date and end_date:
            query = query.filter(and_(
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            ))
        
        if search_term:
            query = query.filter(or_(
                Transaction.transaction_id.ilike(f"%{search_term}%"),
                Transaction.description.ilike(f"%{search_term}%"),
                Transaction.reference_id.ilike(f"%{search_term}%")
            ))
        
        return (
            query
            .order_by(desc(Transaction.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

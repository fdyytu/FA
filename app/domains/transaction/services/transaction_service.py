from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.domains.transaction.models.transaction import Transaction, TransactionStatus, TransactionType
from app.domains.transaction.repositories.transaction_repository import TransactionRepository
from app.domains.transaction.schemas.transaction_schemas import (
    TransactionCreate, TransactionUpdate, TransactionResponse, 
    TransactionListResponse, TransactionStatsResponse
)
from app.common.base_classes.base_service import BaseService
from app.common.responses.api_response import APIResponse

class TransactionService(BaseService):
    def __init__(self, db: Session):
        self.db = db
        self.repository = TransactionRepository(db)
    
    async def create_transaction(self, transaction_data: TransactionCreate) -> APIResponse:
        """Create a new transaction"""
        try:
            transaction = self.repository.create_transaction(transaction_data)
            return APIResponse.success(
                data=TransactionResponse.from_orm(transaction),
                message="Transaction created successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Failed to create transaction: {str(e)}")
    
    async def get_transaction(self, transaction_id: str) -> APIResponse:
        """Get transaction by ID"""
        try:
            transaction = self.repository.get_by_transaction_id(transaction_id)
            if not transaction:
                return APIResponse.error("Transaction not found", status_code=404)
            
            return APIResponse.success(
                data=TransactionResponse.from_orm(transaction)
            )
        except Exception as e:
            return APIResponse.error(f"Failed to get transaction: {str(e)}")
    
    async def update_transaction_status(self, transaction_id: str, status: TransactionStatus, message: Optional[str] = None) -> APIResponse:
        """Update transaction status"""
        try:
            transaction = self.repository.update_transaction_status(transaction_id, status, message)
            if not transaction:
                return APIResponse.error("Transaction not found", status_code=404)
            
            return APIResponse.success(
                data=TransactionResponse.from_orm(transaction),
                message=f"Transaction status updated to {status.value}"
            )
        except Exception as e:
            return APIResponse.error(f"Failed to update transaction status: {str(e)}")
    
    async def get_user_transactions(self, user_id: int, page: int = 1, per_page: int = 20) -> APIResponse:
        """Get transactions for a specific user"""
        try:
            skip = (page - 1) * per_page
            transactions = self.repository.get_by_user_id(user_id, skip=skip, limit=per_page)
            
            # Get total count for pagination
            total = self.db.query(Transaction).filter(Transaction.user_id == user_id).count()
            total_pages = (total + per_page - 1) // per_page
            
            response_data = TransactionListResponse(
                transactions=[TransactionResponse.from_orm(t) for t in transactions],
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )
            
            return APIResponse.success(data=response_data)
        except Exception as e:
            return APIResponse.error(f"Failed to get user transactions: {str(e)}")
    
    async def get_transactions_by_status(self, status: TransactionStatus, page: int = 1, per_page: int = 20) -> APIResponse:
        """Get transactions by status"""
        try:
            skip = (page - 1) * per_page
            transactions = self.repository.get_by_status(status, skip=skip, limit=per_page)
            
            # Get total count for pagination
            total = self.db.query(Transaction).filter(Transaction.status == status).count()
            total_pages = (total + per_page - 1) // per_page
            
            response_data = TransactionListResponse(
                transactions=[TransactionResponse.from_orm(t) for t in transactions],
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )
            
            return APIResponse.success(data=response_data)
        except Exception as e:
            return APIResponse.error(f"Failed to get transactions by status: {str(e)}")
    
    async def get_transactions_by_type(self, transaction_type: TransactionType, page: int = 1, per_page: int = 20) -> APIResponse:
        """Get transactions by type"""
        try:
            skip = (page - 1) * per_page
            transactions = self.repository.get_by_type(transaction_type, skip=skip, limit=per_page)
            
            # Get total count for pagination
            total = self.db.query(Transaction).filter(Transaction.transaction_type == transaction_type).count()
            total_pages = (total + per_page - 1) // per_page
            
            response_data = TransactionListResponse(
                transactions=[TransactionResponse.from_orm(t) for t in transactions],
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )
            
            return APIResponse.success(data=response_data)
        except Exception as e:
            return APIResponse.error(f"Failed to get transactions by type: {str(e)}")
    
    async def search_transactions(self, 
                                user_id: Optional[int] = None,
                                status: Optional[TransactionStatus] = None,
                                transaction_type: Optional[TransactionType] = None,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                search_term: Optional[str] = None,
                                page: int = 1,
                                per_page: int = 20) -> APIResponse:
        """Search transactions with filters"""
        try:
            skip = (page - 1) * per_page
            transactions = self.repository.search_transactions(
                user_id=user_id,
                status=status,
                transaction_type=transaction_type,
                start_date=start_date,
                end_date=end_date,
                search_term=search_term,
                skip=skip,
                limit=per_page
            )
            
            # Get total count for pagination (simplified - could be optimized)
            total_transactions = self.repository.search_transactions(
                user_id=user_id,
                status=status,
                transaction_type=transaction_type,
                start_date=start_date,
                end_date=end_date,
                search_term=search_term,
                skip=0,
                limit=10000  # Large number to get all for count
            )
            total = len(total_transactions)
            total_pages = (total + per_page - 1) // per_page
            
            response_data = TransactionListResponse(
                transactions=[TransactionResponse.from_orm(t) for t in transactions],
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )
            
            return APIResponse.success(data=response_data)
        except Exception as e:
            return APIResponse.error(f"Failed to search transactions: {str(e)}")
    
    async def get_transaction_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> APIResponse:
        """Get transaction statistics"""
        try:
            stats = self.repository.get_transaction_stats(start_date, end_date)
            response_data = TransactionStatsResponse(**stats)
            
            return APIResponse.success(data=response_data)
        except Exception as e:
            return APIResponse.error(f"Failed to get transaction stats: {str(e)}")
    
    async def get_transaction_logs(self, transaction_id: str) -> APIResponse:
        """Get transaction logs"""
        try:
            # First check if transaction exists
            transaction = self.repository.get_by_transaction_id(transaction_id)
            if not transaction:
                return APIResponse.error("Transaction not found", status_code=404)
            
            logs = self.repository.get_transaction_logs(transaction_id)
            return APIResponse.success(data=logs)
        except Exception as e:
            return APIResponse.error(f"Failed to get transaction logs: {str(e)}")
    
    async def cancel_transaction(self, transaction_id: str, reason: Optional[str] = None) -> APIResponse:
        """Cancel a transaction"""
        try:
            transaction = self.repository.get_by_transaction_id(transaction_id)
            if not transaction:
                return APIResponse.error("Transaction not found", status_code=404)
            
            if transaction.status not in [TransactionStatus.PENDING, TransactionStatus.PROCESSING]:
                return APIResponse.error("Transaction cannot be cancelled", status_code=400)
            
            message = f"Transaction cancelled. Reason: {reason}" if reason else "Transaction cancelled"
            updated_transaction = self.repository.update_transaction_status(
                transaction_id, TransactionStatus.CANCELLED, message
            )
            
            return APIResponse.success(
                data=TransactionResponse.from_orm(updated_transaction),
                message="Transaction cancelled successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Failed to cancel transaction: {str(e)}")

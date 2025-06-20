"""
PPOB Transaction Service
Service untuk menangani operasi transaksi PPOB
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from decimal import Decimal

from app.common.base_classes.base_service import BaseService
from app.domains.ppob.repositories.ppob_repository import PPOBRepository
from app.domains.ppob.models.ppob import PPOBTransaction, TransactionStatus
from app.domains.ppob.schemas.ppob_schemas import PPOBTransactionCreate, PPOBTransactionUpdate

# Try to import User from domains
try:
    from app.domains.auth.models.user import User
except ImportError:
    User = None

try:
    from app.cache.managers.ppob_cache_manager import ppob_cache_manager
except ImportError:
    ppob_cache_manager = None


class PPOBTransactionService(BaseService):
    """Service untuk menangani operasi transaksi PPOB"""
    
    def __init__(self, repository: PPOBRepository):
        super().__init__(repository)
    
    async def create_transaction(self, user: User, transaction_data: PPOBTransactionCreate) -> PPOBTransaction:
        """Buat transaksi baru"""
        try:
            # Validate user balance if needed
            if hasattr(user, 'balance') and user.balance < transaction_data.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient balance"
                )
            
            # Create transaction
            transaction = await self.repository.create_transaction({
                **transaction_data.dict(),
                'user_id': user.id,
                'status': TransactionStatus.PENDING
            })
            
            # Clear cache
            if ppob_cache_manager:
                await ppob_cache_manager.delete_pattern(f"user_transactions_{user.id}*")
            
            return transaction
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating transaction: {str(e)}"
            )
    
    def get_user_transactions(
        self, 
        user_id: int, 
        status: Optional[TransactionStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[PPOBTransaction]:
        """Ambil transaksi user"""
        try:
            return self.repository.get_user_transactions(
                user_id=user_id,
                status=status,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user transactions: {str(e)}"
            )
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[PPOBTransaction]:
        """Ambil transaksi berdasarkan ID"""
        try:
            return self.repository.get_transaction_by_id(transaction_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting transaction: {str(e)}"
            )
    
    def get_transaction_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Ambil statistik transaksi"""
        try:
            return self.repository.get_transaction_stats(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting transaction stats: {str(e)}"
            )
    
    async def update_transaction_status(
        self, 
        transaction_id: int, 
        status: TransactionStatus,
        notes: Optional[str] = None
    ) -> PPOBTransaction:
        """Update status transaksi"""
        try:
            transaction = await self.repository.get_transaction_by_id(transaction_id)
            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaction not found"
                )
            
            update_data = PPOBTransactionUpdate(
                status=status,
                notes=notes
            )
            
            updated_transaction = await self.repository.update_transaction(
                transaction_id, update_data.dict(exclude_unset=True)
            )
            
            # Clear cache
            if ppob_cache_manager:
                await ppob_cache_manager.delete_pattern(f"user_transactions_{transaction.user_id}*")
            
            return updated_transaction
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating transaction: {str(e)}"
            )
    
    async def cancel_transaction(self, transaction_id: int, reason: str) -> PPOBTransaction:
        """Batalkan transaksi"""
        try:
            transaction = await self.repository.get_transaction_by_id(transaction_id)
            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaction not found"
                )
            
            if transaction.status != TransactionStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only pending transactions can be cancelled"
                )
            
            return await self.update_transaction_status(
                transaction_id, 
                TransactionStatus.CANCELLED,
                f"Cancelled: {reason}"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error cancelling transaction: {str(e)}"
            )
    
    async def get_transaction_history(
        self, 
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50
    ) -> List[PPOBTransaction]:
        """Ambil riwayat transaksi dengan filter tanggal"""
        try:
            # Check cache first
            if ppob_cache_manager:
                cache_key = f"transaction_history_{user_id}_{start_date}_{end_date}_{limit}"
                cached_history = await ppob_cache_manager.get(cache_key)
                if cached_history:
                    return cached_history
            
            history = await self.repository.get_transaction_history(
                user_id, start_date, end_date, limit
            )
            
            # Cache the result
            if ppob_cache_manager and history:
                await ppob_cache_manager.set(cache_key, history, ttl=300)  # 5 minutes
            
            return history
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting transaction history: {str(e)}"
            )

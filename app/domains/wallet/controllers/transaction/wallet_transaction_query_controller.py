"""
Modul ini berisi implementasi query controller untuk wallet transactions.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.common.responses.api_response import APIResponse
from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.schemas.wallet_schemas import (
    TransactionHistoryResponse,
    TransactionTypeEnum
)
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

router = APIRouter()

@router.get(
    "/transactions",
    response_model=APIResponse[TransactionHistoryResponse],
    summary="Get Transaction History",
    description="Mendapatkan riwayat transaksi wallet"
)
async def get_transaction_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    transaction_type: Optional[TransactionTypeEnum] = None
) -> APIResponse[TransactionHistoryResponse]:
    """Get user's transaction history"""
    try:
        repository = WalletRepository(db)
        service = WalletService(repository)
        
        result = service.get_transaction_history(
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            transaction_type=transaction_type
        )
        
        response_data = TransactionHistoryResponse(**result)
        
        return APIResponse.success_response(
            data=response_data,
            message="Riwayat transaksi berhasil diambil"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil riwayat transaksi: {str(e)}"
        )

__all__ = ['router']

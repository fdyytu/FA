"""
Modul ini berisi implementasi query controller untuk wallet balance.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.responses.api_response import APIResponse
from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.schemas.wallet_schemas import WalletBalanceResponse
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

router = APIRouter()

@router.get(
    "/balance",
    response_model=APIResponse[WalletBalanceResponse],
    summary="Get Wallet Balance",
    description="Mendapatkan saldo wallet pengguna saat ini"
)
async def get_wallet_balance(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> APIResponse[WalletBalanceResponse]:
    """Get current user's wallet balance"""
    try:
        repository = WalletRepository(db)
        service = WalletService(repository)
        
        balance = service.get_user_balance(current_user.id)
        
        response_data = WalletBalanceResponse(
            balance=balance,
            user_id=current_user.id,
            username=current_user.username
        )
        
        return APIResponse.success_response(
            data=response_data,
            message="Saldo wallet berhasil diambil"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil saldo wallet: {str(e)}"
        )

__all__ = ['router']

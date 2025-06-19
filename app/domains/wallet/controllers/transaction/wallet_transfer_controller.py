"""
Modul ini berisi implementasi transfer controller untuk wallet transactions.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.responses.api_response import APIResponse
from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.schemas.wallet_schemas import (
    TransferRequest, TransferResponse
)
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

router = APIRouter()

@router.post(
    "/transfer",
    response_model=APIResponse[TransferResponse],
    summary="Transfer Money",
    description="Transfer uang ke pengguna lain"
)
async def transfer_money(
    transfer_request: TransferRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> APIResponse[TransferResponse]:
    """Transfer money to another user"""
    try:
        repository = WalletRepository(db)
        service = WalletService(repository)
        
        transfer = service.transfer_money(
            sender_id=current_user.id,
            transfer_request=transfer_request
        )
        
        # Get receiver info for response
        receiver = db.query(User).filter(
            User.username == transfer_request.receiver_username
        ).first()
        
        response_data = TransferResponse(
            id=transfer.id,
            transfer_code=transfer.transfer_code,
            sender_username=current_user.username,
            receiver_username=receiver.username,
            amount=transfer.amount,
            status=transfer.status,
            description=transfer.description,
            created_at=transfer.created_at
        )
        
        return APIResponse.success_response(
            data=response_data,
            message="Transfer berhasil dilakukan"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan transfer: {str(e)}"
        )

__all__ = ['router']

"""
Modul ini berisi implementasi Midtrans top-up controller untuk wallet.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.responses.api_response import APIResponse
from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.schemas.wallet_schemas import (
    TopUpMidtransRequest, TopUpMidtransResponse
)
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

router = APIRouter()

@router.post(
    "/topup/midtrans",
    response_model=APIResponse[TopUpMidtransResponse],
    summary="Create Midtrans Top-up",
    description="Membuat pembayaran top-up melalui Midtrans"
)
async def create_midtrans_topup(
    topup_request: TopUpMidtransRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> APIResponse[TopUpMidtransResponse]:
    """Create Midtrans top up payment"""
    try:
        repository = WalletRepository(db)
        service = WalletService(repository)
        
        result = service.create_midtrans_topup(
            user_id=current_user.id,
            topup_request=topup_request
        )
        
        response_data = TopUpMidtransResponse(**result)
        
        return APIResponse.success_response(
            data=response_data,
            message="Pembayaran Midtrans berhasil dibuat"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat pembayaran Midtrans: {str(e)}"
        )

@router.post(
    "/midtrans/notification",
    response_model=APIResponse[dict],
    summary="Midtrans Notification",
    description="Handle notifikasi pembayaran dari Midtrans"
)
async def midtrans_notification(
    notification_data: dict,
    db: Session = Depends(get_db)
) -> APIResponse[dict]:
    """Handle Midtrans payment notification webhook"""
    try:
        repository = WalletRepository(db)
        service = WalletService(repository)
        
        result = service.process_midtrans_notification(notification_data)
        
        if result['success']:
            return APIResponse.success_response(
                data=result,
                message="Notifikasi berhasil diproses"
            )
        else:
            return APIResponse.error_response(
                message="Gagal memproses notifikasi",
                error_code="NOTIFICATION_FAILED"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses notifikasi: {str(e)}"
        )

__all__ = ['router']

"""
Modul ini berisi implementasi admin controller untuk approval top-up wallet.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.common.responses.api_response import APIResponse
from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.schemas.wallet_schemas import (
    TopUpListResponse, TopUpResponse, TopUpApprovalRequest
)
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

router = APIRouter()

@router.get(
    "/topup-requests",
    response_model=APIResponse[List[TopUpListResponse]],
    summary="Get Pending Top-up Requests",
    description="Mendapatkan daftar permintaan top-up yang menunggu persetujuan"
)
async def get_pending_topup_requests(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
) -> APIResponse[List[TopUpListResponse]]:
    """Get pending top up requests (Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses admin diperlukan"
        )
    
    try:
        repository = WalletRepository(db)
        service = WalletService(repository)
        
        result = service.get_pending_topup_requests(page=page, per_page=per_page)
        
        # Convert to response format
        requests_response = []
        for req in result['requests']:
            requests_response.append(TopUpListResponse(
                id=req.id,
                request_code=req.request_code,
                user_username=req.user.username,
                amount=req.amount,
                payment_method=req.payment_method,
                status=req.status,
                bank_name=req.bank_name,
                account_number=req.account_number,
                account_name=req.account_name,
                proof_image=req.proof_image,
                notes=req.notes,
                admin_notes=req.admin_notes,
                created_at=req.created_at,
                processed_at=req.processed_at
            ))
        
        return APIResponse.success_response(
            data=requests_response,
            message="Daftar permintaan top up berhasil diambil"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil daftar permintaan top up: {str(e)}"
        )

@router.put(
    "/topup-requests/{request_id}/approve",
    response_model=APIResponse[TopUpResponse],
    summary="Approve Top-up Request",
    description="Menyetujui atau menolak permintaan top-up"
)
async def approve_topup_request(
    request_id: int,
    approval_request: TopUpApprovalRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> APIResponse[TopUpResponse]:
    """Approve or reject top up request (Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses admin diperlukan"
        )
    
    try:
        repository = WalletRepository(db)
        service = WalletService(repository)
        
        request = service.process_topup_approval(
            request_id=request_id,
            approval_request=approval_request,
            admin_user_id=current_user.id
        )
        
        response_data = TopUpResponse(
            id=request.id,
            request_code=request.request_code,
            amount=request.amount,
            payment_method=request.payment_method,
            status=request.status,
            bank_name=request.bank_name,
            account_number=request.account_number,
            account_name=request.account_name,
            notes=request.notes,
            created_at=request.created_at
        )
        
        return APIResponse.success_response(
            data=response_data,
            message="Permintaan top up berhasil diproses"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses permintaan top up: {str(e)}"
        )

__all__ = ['router']

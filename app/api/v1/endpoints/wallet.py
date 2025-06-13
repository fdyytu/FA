from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.payment.services.payment_factory import PaymentFactory
from app.domains.payment.services.manual_topup_service import ManualTopUpService
from app.schemas.wallet import (
    WalletBalanceResponse, TransferRequest, TransferResponse,
    TopUpManualRequest, TopUpMidtransRequest, TopUpResponse, TopUpMidtransResponse,
    TopUpApprovalRequest, TopUpListResponse, TransactionHistoryResponse,
    WalletTransactionResponse, TransactionTypeEnum
)
from app.models.wallet import PaymentMethod
from app.utils.responses import create_success_response, create_error_response
from app.utils.exceptions import ValidationError, NotFoundError, InsufficientBalanceError

router = APIRouter()

def get_wallet_service(db: Session) -> WalletService:
    """Helper function untuk membuat WalletService instance - mengikuti DRY"""
    wallet_repository = WalletRepository(db)
    return WalletService(wallet_repository)

def get_payment_factory(db: Session) -> PaymentFactory:
    """Helper function untuk membuat PaymentFactory instance - mengikuti DRY"""
    return PaymentFactory(db)

def get_manual_topup_service(db: Session) -> ManualTopUpService:
    """Helper function untuk membuat ManualTopUpService instance - mengikuti DRY"""
    return ManualTopUpService(db)

@router.get("/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's wallet balance"""
    try:
        wallet_service = get_wallet_service(db)
        balance = wallet_service.get_user_balance(current_user.id)
        
        return WalletBalanceResponse(
            balance=balance,
            user_id=current_user.id,
            username=current_user.username
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/transactions", response_model=TransactionHistoryResponse)
async def get_transaction_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    transaction_type: Optional[TransactionTypeEnum] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's transaction history"""
    try:
        wallet_service = get_wallet_service(db)
        result = wallet_service.get_transaction_history(
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            transaction_type=transaction_type
        )
        
        return TransactionHistoryResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/transfer", response_model=TransferResponse)
async def transfer_money(
    transfer_request: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer money to another user"""
    try:
        wallet_service = get_wallet_service(db)
        transfer = wallet_service.transfer_money(
            sender_id=current_user.id,
            transfer_request=transfer_request
        )
        
        # Get receiver info for response
        receiver = db.query(User).filter(
            User.username == transfer_request.receiver_username
        ).first()
        
        return TransferResponse(
            id=transfer.id,
            transfer_code=transfer.transfer_code,
            sender_username=current_user.username,
            receiver_username=receiver.username,
            amount=transfer.amount,
            status=transfer.status,
            description=transfer.description,
            created_at=transfer.created_at
        )
    except (ValidationError, NotFoundError, InsufficientBalanceError) as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/topup/manual", response_model=TopUpResponse)
async def create_manual_topup(
    topup_request: TopUpManualRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create manual top up request - menggunakan PaymentFactory"""
    try:
        payment_factory = get_payment_factory(db)
        result = payment_factory.process_payment(
            payment_method=topup_request.payment_method,
            user_id=current_user.id,
            amount=topup_request.amount,
            bank_name=topup_request.bank_name,
            account_number=topup_request.account_number,
            account_name=topup_request.account_name,
            notes=topup_request.notes
        )
        
        return TopUpResponse(
            request_code=result['request_code'],
            amount=result['amount'],
            payment_method=result['payment_method'],
            status=result['status'],
            bank_name=result.get('bank_name'),
            account_number=result.get('account_number')
        )
    except ValidationError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/topup/midtrans", response_model=TopUpMidtransResponse)
async def create_midtrans_topup(
    topup_request: TopUpMidtransRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Midtrans top up payment - menggunakan PaymentFactory"""
    try:
        payment_factory = get_payment_factory(db)
        result = payment_factory.process_payment(
            payment_method=PaymentMethod.MIDTRANS,
            user_id=current_user.id,
            amount=topup_request.amount
        )
        
        return TopUpMidtransResponse(
            request_code=result['request_code'],
            amount=result['amount'],
            midtrans_order_id=result['midtrans_order_id'],
            payment_url=result['payment_url'],
            status=result['status']
        )
    except ValidationError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/topup/requests")
async def get_pending_topup_requests(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending top up requests (Admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        manual_service = get_manual_topup_service(db)
        offset = (page - 1) * per_page
        requests = manual_service.get_pending_requests(limit=per_page, offset=offset)
        
        return create_success_response(
            data={
                "requests": [
                    {
                        "id": req.id,
                        "request_code": req.request_code,
                        "user_id": req.user_id,
                        "amount": req.amount,
                        "payment_method": req.payment_method,
                        "bank_name": req.bank_name,
                        "account_number": req.account_number,
                        "account_name": req.account_name,
                        "notes": req.notes,
                        "status": req.status,
                        "created_at": req.created_at
                    } for req in requests
                ],
                "page": page,
                "per_page": per_page,
                "total": len(requests)
            },
            message="Pending top up requests retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/topup/approve/{request_id}")
async def approve_topup_request(
    request_id: int,
    approval_request: TopUpApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve or reject top up request (Admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        manual_service = get_manual_topup_service(db)
        
        if approval_request.status.value == "APPROVED":
            request = manual_service.approve_topup_request(
                request_id=request_id,
                admin_user_id=current_user.id,
                admin_notes=approval_request.admin_notes
            )
        else:
            request = manual_service.reject_topup_request(
                request_id=request_id,
                admin_user_id=current_user.id,
                admin_notes=approval_request.admin_notes
            )
        
        return create_success_response(
            data={
                "id": request.id,
                "request_code": request.request_code,
                "status": request.status,
                "admin_notes": request.admin_notes,
                "processed_at": request.processed_at
            },
            message=f"Top up request {approval_request.status.value.lower()} successfully"
        )
    except (ValidationError, NotFoundError) as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

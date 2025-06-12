from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.wallet_service import WalletService
from app.schemas.wallet import (
    WalletBalanceResponse, TransferRequest, TransferResponse,
    TopUpManualRequest, TopUpMidtransRequest, TopUpResponse, TopUpMidtransResponse,
    TopUpApprovalRequest, TopUpListResponse, TransactionHistoryResponse,
    WalletTransactionResponse, TransactionTypeEnum
)
from app.utils.responses import create_success_response, create_error_response
from app.utils.exceptions import ValidationError, NotFoundError, InsufficientBalanceError
import os
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's wallet balance"""
    try:
        wallet_service = WalletService(db)
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
        wallet_service = WalletService(db)
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
        wallet_service = WalletService(db)
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
    """Create manual top up request"""
    try:
        wallet_service = WalletService(db)
        request = wallet_service.create_manual_topup_request(
            user_id=current_user.id,
            topup_request=topup_request
        )
        
        return TopUpResponse(
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
    except ValidationError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/topup/manual/{request_id}/upload-proof")
async def upload_topup_proof(
    request_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload proof of payment for manual top up"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if file.content_type not in allowed_types:
            raise ValidationError("Only JPEG and PNG images are allowed")
        
        # Check file size (max 5MB)
        if file.size > 5 * 1024 * 1024:
            raise ValidationError("File size must be less than 5MB")
        
        # Find top up request
        from app.models.wallet import TopUpRequest, TopUpStatus
        request = db.query(TopUpRequest).filter(
            TopUpRequest.id == request_id,
            TopUpRequest.user_id == current_user.id,
            TopUpRequest.status == TopUpStatus.PENDING
        ).first()
        
        if not request:
            raise NotFoundError("Top up request not found or already processed")
        
        # Create upload directory if not exists
        upload_dir = "uploads/topup_proofs"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        filename = f"{request.request_code}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update request with proof image path
        request.proof_image = file_path
        db.commit()
        
        return create_success_response(
            message="Proof of payment uploaded successfully",
            data={"filename": filename, "path": file_path}
        )
        
    except (ValidationError, NotFoundError) as e:
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
    """Create Midtrans top up payment"""
    try:
        wallet_service = WalletService(db)
        result = wallet_service.create_midtrans_topup(
            user_id=current_user.id,
            topup_request=topup_request
        )
        
        return TopUpMidtransResponse(**result)
    except ValidationError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/midtrans/notification")
async def midtrans_notification(
    notification_data: dict,
    db: Session = Depends(get_db)
):
    """Handle Midtrans payment notification webhook"""
    try:
        wallet_service = WalletService(db)
        result = wallet_service.process_midtrans_notification(notification_data)
        
        if result['success']:
            return create_success_response(
                message="Notification processed successfully",
                data=result
            )
        else:
            return create_error_response(
                message="Failed to process notification",
                errors={"error": result['error']}
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Admin endpoints
@router.get("/admin/topup-requests", response_model=List[TopUpListResponse])
async def get_pending_topup_requests(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending top up requests (Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        wallet_service = WalletService(db)
        result = wallet_service.get_pending_topup_requests(page=page, per_page=per_page)
        
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
        
        return requests_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/admin/topup-requests/{request_id}/approve", response_model=TopUpResponse)
async def approve_topup_request(
    request_id: int,
    approval_request: TopUpApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve or reject top up request (Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        wallet_service = WalletService(db)
        request = wallet_service.process_topup_approval(
            request_id=request_id,
            approval_request=approval_request,
            admin_user_id=current_user.id
        )
        
        return TopUpResponse(
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
    except (ValidationError, NotFoundError) as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

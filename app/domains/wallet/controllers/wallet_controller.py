from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from app.common.base_classes.base_controller import BaseController
from app.common.responses.api_response import APIResponse
from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.schemas.wallet_schemas import (
    WalletBalanceResponse, TransferRequest, TransferResponse,
    TopUpManualRequest, TopUpMidtransRequest, TopUpResponse, TopUpMidtransResponse,
    TopUpApprovalRequest, TopUpListResponse, TransactionHistoryResponse,
    WalletTransactionResponse, TransactionTypeEnum, WalletTransactionCreate, WalletTransactionUpdate
)
from app.domains.wallet.models.wallet import WalletTransaction
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User
import os
import uuid
from datetime import datetime

class WalletController:
    """
    Wallet Controller yang mengimplementasikan Single Responsibility Principle.
    Menangani semua endpoint terkait wallet dan transaksi keuangan.
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/wallet", tags=["Wallet"])
        self._setup_wallet_routes()
    
    def _setup_wallet_routes(self):
        """Setup routes khusus untuk wallet"""
        self.router.add_api_route(
            "/balance",
            self.get_wallet_balance,
            methods=["GET"],
            response_model=APIResponse[WalletBalanceResponse]
        )
        self.router.add_api_route(
            "/transactions",
            self.get_transaction_history,
            methods=["GET"],
            response_model=APIResponse[TransactionHistoryResponse]
        )
        self.router.add_api_route(
            "/transfer",
            self.transfer_money,
            methods=["POST"],
            response_model=APIResponse[TransferResponse]
        )
        self.router.add_api_route(
            "/topup/manual",
            self.create_manual_topup,
            methods=["POST"],
            response_model=APIResponse[TopUpResponse]
        )
        self.router.add_api_route(
            "/topup/manual/{request_id}/upload-proof",
            self.upload_topup_proof,
            methods=["POST"],
            response_model=APIResponse[TopUpResponse]
        )
        self.router.add_api_route(
            "/topup/midtrans",
            self.create_midtrans_topup,
            methods=["POST"],
            response_model=APIResponse[TopUpMidtransResponse]
        )
        self.router.add_api_route(
            "/midtrans/notification",
            self.midtrans_notification,
            methods=["POST"],
            response_model=APIResponse[dict]
        )
        # Admin routes
        self.router.add_api_route(
            "/admin/topup-requests",
            self.get_pending_topup_requests,
            methods=["GET"],
            response_model=APIResponse[List[TopUpListResponse]]
        )
        self.router.add_api_route(
            "/admin/topup-requests/{request_id}/approve",
            self.approve_topup_request,
            methods=["PUT"],
            response_model=APIResponse[TopUpResponse]
        )
    
    async def get_wallet_balance(
        self,
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

    async def get_transaction_history(
        self,
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

    async def transfer_money(
        self,
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

    async def create_manual_topup(
        self,
        topup_request: TopUpManualRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[TopUpResponse]:
        """Create manual top up request"""
        try:
            repository = WalletRepository(db)
            service = WalletService(repository)
            
            request = service.create_manual_topup_request(
                user_id=current_user.id,
                topup_request=topup_request
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
                message="Permintaan top up manual berhasil dibuat"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat permintaan top up: {str(e)}"
            )

    async def upload_topup_proof(
        self,
        request_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db),
        file: UploadFile = File(...)
    ) -> APIResponse[TopUpResponse]:
        """Upload proof of payment for manual top up"""
        try:
            repository = WalletRepository(db)
            service = WalletService(repository)
            
            # Validate file
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File harus berupa gambar"
                )
            
            # Save file
            upload_dir = "static/uploads/topup_proofs"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_extension = file.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(upload_dir, filename)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Update request with proof
            request = service.upload_topup_proof(
                request_id=request_id,
                user_id=current_user.id,
                proof_image_path=file_path
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
                message="Bukti pembayaran berhasil diupload"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal upload bukti pembayaran: {str(e)}"
            )

    async def create_midtrans_topup(
        self,
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

    async def midtrans_notification(
        self,
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

    async def get_pending_topup_requests(
        self,
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

    async def approve_topup_request(
        self,
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

# Instance controller
wallet_controller = WalletController()
router = wallet_controller.router

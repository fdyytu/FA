from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
import os
import uuid

from app.common.responses.api_response import APIResponse
from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.schemas.wallet_schemas import (
    TopUpManualRequest, TopUpMidtransRequest, TopUpResponse, TopUpMidtransResponse
)
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

class WalletTopUpController:
    """Controller untuk menangani operasi top-up wallet"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk top-up"""
        self.router.add_api_route(
            "/topup/manual",
            self.create_manual_topup,
            methods=["POST"],
            response_model=APIResponse[TopUpResponse],
            summary="Create Manual Top-up",
            description="Membuat permintaan top-up manual"
        )
        self.router.add_api_route(
            "/topup/manual/{request_id}/upload-proof",
            self.upload_topup_proof,
            methods=["POST"],
            response_model=APIResponse[TopUpResponse],
            summary="Upload Top-up Proof",
            description="Upload bukti pembayaran untuk top-up manual"
        )
        self.router.add_api_route(
            "/topup/midtrans",
            self.create_midtrans_topup,
            methods=["POST"],
            response_model=APIResponse[TopUpMidtransResponse],
            summary="Create Midtrans Top-up",
            description="Membuat pembayaran top-up melalui Midtrans"
        )
        self.router.add_api_route(
            "/midtrans/notification",
            self.midtrans_notification,
            methods=["POST"],
            response_model=APIResponse[dict],
            summary="Midtrans Notification",
            description="Handle notifikasi pembayaran dari Midtrans"
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

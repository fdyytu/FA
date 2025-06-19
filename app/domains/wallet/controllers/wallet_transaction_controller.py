from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.common.responses.api_response import APIResponse
from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.repositories.wallet_repository import WalletRepository
from app.domains.wallet.schemas.wallet_schemas import (
    TransactionHistoryResponse, TransferRequest, TransferResponse,
    TransactionTypeEnum
)
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

class WalletTransactionController:
    """Controller untuk menangani operasi transaksi wallet"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk transaksi"""
        self.router.add_api_route(
            "/transactions",
            self.get_transaction_history,
            methods=["GET"],
            response_model=APIResponse[TransactionHistoryResponse],
            summary="Get Transaction History",
            description="Mendapatkan riwayat transaksi wallet"
        )
        self.router.add_api_route(
            "/transfer",
            self.transfer_money,
            methods=["POST"],
            response_model=APIResponse[TransferResponse],
            summary="Transfer Money",
            description="Transfer uang ke pengguna lain"
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

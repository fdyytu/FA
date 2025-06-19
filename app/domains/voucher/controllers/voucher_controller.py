from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.common.responses.api_response import APIResponse
from app.domains.voucher.services.voucher_service import VoucherService
from app.domains.voucher.repositories.voucher_repository import VoucherRepository
from app.domains.voucher.schemas.voucher_schemas import (
    VoucherCreate, VoucherUpdate, VoucherResponse, VoucherValidationRequest,
    VoucherValidationResponse, VoucherUsageResponse, VoucherStatsResponse
)
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

class VoucherController:
    """
    Voucher Controller - mengikuti SRP.
    Menangani semua endpoint terkait voucher/promo.
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/vouchers", tags=["Vouchers"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk voucher"""
        # Admin routes
        self.router.add_api_route(
            "/",
            self.create_voucher,
            methods=["POST"],
            response_model=APIResponse[VoucherResponse]
        )
        self.router.add_api_route(
            "/",
            self.get_vouchers,
            methods=["GET"],
            response_model=APIResponse[List[VoucherResponse]]
        )
        self.router.add_api_route(
            "/{voucher_id}",
            self.update_voucher,
            methods=["PUT"],
            response_model=APIResponse[VoucherResponse]
        )
        self.router.add_api_route(
            "/stats",
            self.get_voucher_stats,
            methods=["GET"],
            response_model=APIResponse[VoucherStatsResponse]
        )
        
        # User routes
        self.router.add_api_route(
            "/validate",
            self.validate_voucher,
            methods=["POST"],
            response_model=APIResponse[VoucherValidationResponse]
        )
        self.router.add_api_route(
            "/available",
            self.get_available_vouchers,
            methods=["GET"],
            response_model=APIResponse[List[VoucherResponse]]
        )
        self.router.add_api_route(
            "/my-usage",
            self.get_my_voucher_usage,
            methods=["GET"],
            response_model=APIResponse[List[VoucherUsageResponse]]
        )
    
    async def create_voucher(
        self,
        voucher_data: VoucherCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[VoucherResponse]:
        """Buat voucher baru (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = VoucherRepository(db)
            service = VoucherService(repository)
            
            voucher = await service.create_voucher(voucher_data)
            
            return APIResponse.success_response(
                data=voucher,
                message="Voucher berhasil dibuat"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat voucher: {str(e)}"
            )
    
    async def get_vouchers(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[List[VoucherResponse]]:
        """Ambil semua voucher (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = VoucherRepository(db)
            vouchers = repository.get_all()
            
            return APIResponse.success_response(
                data=vouchers,
                message="Daftar voucher berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil voucher: {str(e)}"
            )
    
    async def update_voucher(
        self,
        voucher_id: int,
        voucher_data: VoucherUpdate,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[VoucherResponse]:
        """Update voucher (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = VoucherRepository(db)
            
            voucher = repository.get_by_id(voucher_id)
            if not voucher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Voucher tidak ditemukan"
                )
            
            updated_voucher = repository.update(voucher_id, voucher_data.dict(exclude_unset=True))
            
            return APIResponse.success_response(
                data=updated_voucher,
                message="Voucher berhasil diupdate"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal update voucher: {str(e)}"
            )
    
    async def validate_voucher(
        self,
        request: VoucherValidationRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[VoucherValidationResponse]:
        """Validasi voucher untuk transaksi"""
        try:
            repository = VoucherRepository(db)
            service = VoucherService(repository)
            
            result = await service.validate_voucher(request, current_user.id)
            
            return APIResponse.success_response(
                data=result,
                message="Validasi voucher selesai"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal validasi voucher: {str(e)}"
            )
    
    async def get_available_vouchers(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[List[VoucherResponse]]:
        """Ambil voucher yang tersedia untuk user"""
        try:
            repository = VoucherRepository(db)
            service = VoucherService(repository)
            
            vouchers = await service.get_user_vouchers(current_user.id)
            
            return APIResponse.success_response(
                data=vouchers,
                message="Voucher tersedia berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil voucher: {str(e)}"
            )
    
    async def get_my_voucher_usage(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[List[VoucherUsageResponse]]:
        """Ambil riwayat penggunaan voucher user"""
        try:
            repository = VoucherRepository(db)
            
            usage_history = repository.get_user_voucher_history(current_user.id)
            
            return APIResponse.success_response(
                data=usage_history,
                message="Riwayat voucher berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil riwayat: {str(e)}"
            )
    
    async def get_voucher_stats(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[VoucherStatsResponse]:
        """Ambil statistik voucher (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = VoucherRepository(db)
            service = VoucherService(repository)
            
            stats = await service.get_voucher_stats()
            
            return APIResponse.success_response(
                data=stats,
                message="Statistik voucher berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil statistik: {str(e)}"
            )

# Instance controller
voucher_controller = VoucherController()
router = voucher_controller.router

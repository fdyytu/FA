from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.shared.base_classes.base_controller import BaseController
from app.shared.responses.api_response import APIResponse
from app.domains.ppob.services.ppob_service import PPOBService
from app.domains.ppob.repositories.ppob_repository import PPOBRepository
from app.domains.ppob.schemas.ppob_schemas import (
    PPOBInquiryRequest, PPOBInquiryResponse, PPOBPaymentRequest,
    PPOBTransactionCreate, PPOBTransactionUpdate, PPOBTransactionResponse,
    PPOBProductResponse, PPOBCategoryResponse, TransactionHistoryResponse,
    PPOBStatsResponse, PopularProductResponse, MonthlyRevenueResponse
)
from app.domains.ppob.models.ppob import PPOBTransaction, PPOBCategory, TransactionStatus
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

class PPOBController:
    """
    PPOB Controller yang mengimplementasikan Single Responsibility Principle.
    Menangani semua endpoint terkait PPOB (Payment Point Online Bank).
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/ppob", tags=["PPOB"])
        self._setup_ppob_routes()
    
    def _setup_ppob_routes(self):
        """Setup routes khusus untuk PPOB"""
        # Product routes
        self.router.add_api_route(
            "/categories",
            self.get_categories,
            methods=["GET"],
            response_model=APIResponse[List[PPOBCategoryResponse]]
        )
        self.router.add_api_route(
            "/products/{category}",
            self.get_products_by_category,
            methods=["GET"],
            response_model=APIResponse[List[PPOBProductResponse]]
        )
        self.router.add_api_route(
            "/products/code/{product_code}",
            self.get_product_by_code,
            methods=["GET"],
            response_model=APIResponse[PPOBProductResponse]
        )
        
        # Transaction routes
        self.router.add_api_route(
            "/inquiry",
            self.inquiry,
            methods=["POST"],
            response_model=APIResponse[PPOBInquiryResponse]
        )
        self.router.add_api_route(
            "/payment",
            self.payment,
            methods=["POST"],
            response_model=APIResponse[PPOBTransactionResponse]
        )
        self.router.add_api_route(
            "/transactions",
            self.get_user_transactions,
            methods=["GET"],
            response_model=APIResponse[TransactionHistoryResponse]
        )
        self.router.add_api_route(
            "/transactions/{transaction_id}",
            self.get_transaction_detail,
            methods=["GET"],
            response_model=APIResponse[PPOBTransactionResponse]
        )
        self.router.add_api_route(
            "/transactions/{transaction_id}/cancel",
            self.cancel_transaction,
            methods=["PUT"],
            response_model=APIResponse[PPOBTransactionResponse]
        )
        self.router.add_api_route(
            "/transactions/{transaction_id}/retry",
            self.retry_transaction,
            methods=["PUT"],
            response_model=APIResponse[PPOBTransactionResponse]
        )
        
        # Statistics routes
        self.router.add_api_route(
            "/stats",
            self.get_transaction_stats,
            methods=["GET"],
            response_model=APIResponse[PPOBStatsResponse],
            operation_id="get_ppob_transaction_stats"
        )
        self.router.add_api_route(
            "/popular-products",
            self.get_popular_products,
            methods=["GET"],
            response_model=APIResponse[List[PopularProductResponse]]
        )
        
        # Admin routes
        self.router.add_api_route(
            "/admin/stats",
            self.get_admin_stats,
            methods=["GET"],
            response_model=APIResponse[PPOBStatsResponse],
            operation_id="get_ppob_admin_stats"
        )
        self.router.add_api_route(
            "/admin/revenue/{year}/{month}",
            self.get_monthly_revenue,
            methods=["GET"],
            response_model=APIResponse[MonthlyRevenueResponse]
        )
    
    async def get_categories(
        self,
        db: Session = Depends(get_db)
    ) -> APIResponse[List[PPOBCategoryResponse]]:
        """Get available PPOB categories"""
        try:
            categories = []
            for category in PPOBCategory:
                categories.append(PPOBCategoryResponse(
                    value=category.value,
                    name=category.value.replace('_', ' ').title()
                ))
            
            return APIResponse.success_response(
                data=categories,
                message="Kategori PPOB berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil kategori: {str(e)}"
            )

    async def get_products_by_category(
        self,
        category: PPOBCategory,
        db: Session = Depends(get_db)
    ) -> APIResponse[List[PPOBProductResponse]]:
        """Get products by category"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            products = await service.get_products_by_category(category)
            
            return APIResponse.success_response(
                data=products,
                message=f"Produk kategori {category.value} berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil produk: {str(e)}"
            )

    async def get_product_by_code(
        self,
        product_code: str,
        db: Session = Depends(get_db)
    ) -> APIResponse[PPOBProductResponse]:
        """Get product by code"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            product = await service.get_product_by_code(product_code)
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success_response(
                data=product,
                message="Produk berhasil diambil"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil produk: {str(e)}"
            )

    async def inquiry(
        self,
        request: PPOBInquiryRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[PPOBInquiryResponse]:
        """Inquiry PPOB bill"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            result = await service.inquiry(request)
            
            return APIResponse.success_response(
                data=result,
                message="Inquiry berhasil dilakukan"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal melakukan inquiry: {str(e)}"
            )

    async def payment(
        self,
        request: PPOBPaymentRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[PPOBTransactionResponse]:
        """Process PPOB payment"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            # Buat transaksi
            transaction = await service.create_transaction(current_user, request)
            
            # Proses pembayaran
            processed_transaction = await service.process_payment(transaction.id)
            
            return APIResponse.success_response(
                data=processed_transaction,
                message="Pembayaran berhasil diproses"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memproses pembayaran: {str(e)}"
            )

    async def get_user_transactions(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        status: Optional[TransactionStatus] = None,
        category: Optional[PPOBCategory] = None
    ) -> APIResponse[TransactionHistoryResponse]:
        """Get user's PPOB transaction history"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            skip = (page - 1) * limit
            transactions = service.get_user_transactions(
                user_id=current_user.id,
                skip=skip,
                limit=limit,
                status=status,
                category=category
            )
            
            total = repository.count_user_transactions(
                user_id=current_user.id,
                status=status,
                category=category
            )
            
            response_data = TransactionHistoryResponse(
                transactions=transactions,
                total=total,
                page=page,
                size=limit
            )
            
            return APIResponse.success_response(
                data=response_data,
                message="Riwayat transaksi berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil riwayat transaksi: {str(e)}"
            )

    async def get_transaction_detail(
        self,
        transaction_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[PPOBTransactionResponse]:
        """Get transaction detail"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            transaction = service.get_transaction_by_id(transaction_id)
            
            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaksi tidak ditemukan"
                )
            
            if transaction.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tidak memiliki akses ke transaksi ini"
                )
            
            return APIResponse.success_response(
                data=transaction,
                message="Detail transaksi berhasil diambil"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil detail transaksi: {str(e)}"
            )

    async def cancel_transaction(
        self,
        transaction_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[PPOBTransactionResponse]:
        """Cancel transaction"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            transaction = await service.cancel_transaction(transaction_id, current_user.id)
            
            return APIResponse.success_response(
                data=transaction,
                message="Transaksi berhasil dibatalkan"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membatalkan transaksi: {str(e)}"
            )

    async def retry_transaction(
        self,
        transaction_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[PPOBTransactionResponse]:
        """Retry failed transaction"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            transaction = await service.retry_failed_transaction(transaction_id)
            
            return APIResponse.success_response(
                data=transaction,
                message="Transaksi berhasil di-retry"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal retry transaksi: {str(e)}"
            )

    async def get_transaction_stats(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[PPOBStatsResponse]:
        """Get user's transaction statistics"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            stats = service.get_transaction_stats(user_id=current_user.id)
            
            return APIResponse.success_response(
                data=stats,
                message="Statistik transaksi berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil statistik: {str(e)}"
            )

    async def get_popular_products(
        self,
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50)
    ) -> APIResponse[List[PopularProductResponse]]:
        """Get popular products"""
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            products = service.get_popular_products(limit=limit)
            
            return APIResponse.success_response(
                data=products,
                message="Produk populer berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil produk populer: {str(e)}"
            )

    async def get_admin_stats(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[PPOBStatsResponse]:
        """Get admin statistics (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            stats = service.get_transaction_stats()  # All users
            
            return APIResponse.success_response(
                data=stats,
                message="Statistik admin berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil statistik admin: {str(e)}"
            )

    async def get_monthly_revenue(
        self,
        year: int,
        month: int,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[MonthlyRevenueResponse]:
        """Get monthly revenue (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = PPOBRepository(db)
            service = PPOBService(repository)
            
            revenue = service.get_monthly_revenue(year, month)
            
            return APIResponse.success_response(
                data=revenue,
                message="Revenue bulanan berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil revenue bulanan: {str(e)}"
            )

# Instance controller
ppob_controller = PPOBController()
router = ppob_controller.router

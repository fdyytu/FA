from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """
    Standardized API response format untuk konsistensi.
    Mengimplementasikan DRY principle dengan response format yang reusable.
    """
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[dict] = None
    meta: Optional[dict] = None
    
    @classmethod
    def success_response(
        cls, 
        data: T, 
        message: str = "Operasi berhasil",
        meta: Optional[dict] = None
    ) -> "APIResponse[T]":
        """Factory method untuk response sukses"""
        return cls(
            success=True,
            message=message,
            data=data,
            meta=meta
        )
    
    @classmethod
    def error_response(
        cls,
        message: str = "Terjadi kesalahan",
        errors: Optional[dict] = None,
        meta: Optional[dict] = None
    ) -> "APIResponse[None]":
        """Factory method untuk response error"""
        return cls(
            success=False,
            message=message,
            errors=errors,
            meta=meta
        )
    
    @classmethod
    def validation_error_response(
        cls,
        errors: dict,
        message: str = "Validasi gagal"
    ) -> "APIResponse[None]":
        """Factory method untuk validation error response"""
        return cls(
            success=False,
            message=message,
            errors=errors
        )
    
    @classmethod
    def not_found_response(
        cls,
        message: str = "Data tidak ditemukan"
    ) -> "APIResponse[None]":
        """Factory method untuk not found response"""
        return cls(
            success=False,
            message=message
        )
    
    @classmethod
    def paginated_response(
        cls,
        data: T,
        total: int,
        page: int,
        per_page: int,
        message: str = "Data berhasil diambil"
    ) -> "APIResponse[T]":
        """Factory method untuk paginated response"""
        total_pages = (total + per_page - 1) // per_page
        meta = {
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        return cls(
            success=True,
            message=message,
            data=data,
            meta=meta
        )

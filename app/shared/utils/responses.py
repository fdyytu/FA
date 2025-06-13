from typing import Any, Optional, Dict
from pydantic import BaseModel

class APIResponse(BaseModel):
    """Standard API Response format"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[Dict[str, Any]] = None

class SuccessResponse(APIResponse):
    """Response untuk operasi berhasil"""
    def __init__(self, message: str = "Operation successful", data: Any = None):
        super().__init__(success=True, message=message, data=data)

class ErrorResponse(APIResponse):
    """Response untuk operasi gagal"""
    def __init__(self, message: str = "Operation failed", errors: Dict[str, Any] = None):
        super().__init__(success=False, message=message, errors=errors)

class PaginatedResponse(BaseModel):
    """Response untuk data dengan pagination"""
    success: bool = True
    message: str = "Data retrieved successfully"
    data: Any
    pagination: Dict[str, int]
    
    def __init__(self, data: Any, total: int, page: int, size: int, **kwargs):
        pagination_info = {
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size if size > 0 else 0
        }
        super().__init__(data=data, pagination=pagination_info, **kwargs)

def create_success_response(message: str = "Success", data: Any = None) -> Dict[str, Any]:
    """Helper function untuk membuat success response"""
    return {
        "success": True,
        "message": message,
        "data": data
    }

def create_error_response(message: str = "Error", errors: Dict[str, Any] = None) -> Dict[str, Any]:
    """Helper function untuk membuat error response"""
    return {
        "success": False,
        "message": message,
        "errors": errors
    }

def create_paginated_response(
    data: Any, 
    total: int, 
    page: int, 
    size: int,
    message: str = "Data retrieved successfully"
) -> Dict[str, Any]:
    """Helper function untuk membuat paginated response"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size if size > 0 else 0
        }
    }

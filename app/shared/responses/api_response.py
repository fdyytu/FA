from typing import Any, Optional, Dict, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standardized API response model"""
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    errors: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_response(cls, data: Optional[T] = None, message: str = "Success") -> "APIResponse[T]":
        """Create success response"""
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error_response(cls, message: str = "Error", errors: Optional[Dict[str, Any]] = None) -> "APIResponse[T]":
        """Create error response"""
        return cls(success=False, message=message, errors=errors)

def create_response(
    success: bool = True,
    message: str = "Success",
    data: Optional[Any] = None,
    errors: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized API response"""
    response = {
        "success": success,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    if errors is not None:
        response["errors"] = errors
    
    return response
